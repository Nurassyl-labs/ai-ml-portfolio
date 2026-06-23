import os
import sys
from dotenv import load_dotenv
load_dotenv()
import time
import math
import numpy as np
import faiss
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from sentence_transformers import SentenceTransformer

# Try importing fitz for PDF support, print error if not available
try:
    import fitz  # PyMuPDF
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("WARNING: PyMuPDF is not installed. PDF parsing will be unavailable.")

app = Flask(__name__)
# Enable CORS for all routes to support standalone frontends
CORS(app)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
ALLOWED_EXTENSIONS = {'txt', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create data directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize SentenceTransformer model (multilingual MiniLM L12)
# Dimension of this model is 384
EMBEDDING_DIM = 384
print("Loading Embedding Model (paraphrase-multilingual-MiniLM-L12-v2)...")
try:
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    print("Embedding model loaded successfully.")
except Exception as e:
    print(f"Error loading embedding model: {e}")
    sys.exit(1)

# Initialize FAISS Index
# We will use IndexFlatL2 for L2 distance similarity
index = faiss.IndexFlatL2(EMBEDDING_DIM)

# Document storage
# Structure: { filename: { "chunks": [...], "size_bytes": 123 } }
documents = {}
# Chunk mapping to keep track of chunk metadata in index
# Index ID matches position in list
chunks_metadata = []

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def chunk_text(text, chunk_size=350, overlap=50):
    """
    Split text into overlapping chunks
    """
    chunks = []
    if not text:
        return chunks
    
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start += chunk_size - overlap
    return chunks

def process_file(filepath):
    """
    Parse TXT or PDF file and return chunks
    """
    filename = os.path.basename(filepath)
    ext = filename.rsplit('.', 1)[1].lower()
    
    text = ""
    if ext == 'txt':
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
    elif ext == 'pdf':
        if PDF_SUPPORT:
            try:
                doc = fitz.open(filepath)
                for page in doc:
                    text += page.get_text() + "\n"
            except Exception as e:
                print(f"Error parsing PDF {filename}: {e}")
        else:
            text = f"PDF parsing is not enabled. Cannot extract text from {filename}."
            
    # Clean up whitespace
    text = "\n".join([line.strip() for line in text.split("\n") if line.strip()])
    return chunk_text(text)

def add_document_to_index(filename, filepath):
    """
    Parse a file, chunk it, embed it, and add to FAISS index
    """
    global index, chunks_metadata, documents
    
    # Process file to get chunks
    chunks = process_file(filepath)
    if not chunks:
        return 0
        
    size_bytes = os.path.getsize(filepath)
    
    # Store document info
    documents[filename] = {
        "chunks_count": len(chunks),
        "size_bytes": size_bytes,
        "type": filename.rsplit('.', 1)[1].lower()
    }
    
    # Vectorize chunks
    embeddings = model.encode(chunks)
    embeddings = np.array(embeddings).astype('float32')
    
    # Add to FAISS index
    start_id = len(chunks_metadata)
    index.add(embeddings)
    
    # Record metadata
    for i, chunk in enumerate(chunks):
        chunks_metadata.append({
            "id": start_id + i,
            "file": filename,
            "text": chunk
        })
        
    print(f"Added {filename} to index: {len(chunks)} chunks, size {size_bytes} bytes.")
    return len(chunks)

def initialize_default_documents():
    """
    Create sample documents in the data folder if empty,
    so that the system works out-of-the-box with beautiful RAG data!
    """
    # Check if there are already files in the directory
    existing_files = [f for f in os.listdir(UPLOAD_FOLDER) if allowed_file(f)]
    
    if not existing_files:
        print("Data directory is empty. Generating default course materials...")
        
        # 1. 信息存储与检索.txt
        doc1_content = """信息存储与检索是计算机科学与信息管理领域的核心课程。
传统检索主要依赖“关键词匹配”（Keyword Matching），即查找文档中是否包含用户查询的完全相同词汇。这导致了诸如“同义词无法匹配”（如同义词 电脑 与 计算机）和“多义词误匹配”的问题。
而现代智能检索则广泛应用“语义匹配”（Semantic Search）技术。语义匹配的核心是将文本转换到高维的“向量空间模型”（Vector Space Model）中。在这种表示法下，相似含义的词语、句子在空间中的距离会非常接近，即使它们使用的是不同的字眼。
信息检索系统的重要评估指标包括：
1. 查准率（Precision）：检索出的相关文档数占检索出的全部文档数的比例。
2. 查全率（Recall）：检索出的相关文档数占知识库中全部相关文档数的比例。
在实际应用中，往往需要在查准率与查全率之间取得某种平衡（如使用 F1-Score 指标）。"""
        
        with open(os.path.join(UPLOAD_FOLDER, "信息存储与检索.txt"), "w", encoding="utf-8") as f:
            f.write(doc1_content)
            
        # 2. RAG技术综述.txt
        doc2_content = """RAG（Retrieval-Augmented Generation，检索增强生成）是当前大语言模型（LLM）落地应用的最主流架构之一。
大语言模型虽然强大，但存在两大致命缺陷：第一是“幻觉”（Hallucination），即一本正经地胡说八道；第二是“时效性差”，无法掌握训练数据截止日期之后的最新知识，或是企业/个人的私有知识。
RAG 通过“先检索，再生成”的机制完美解决了这些痛点。其核心流程如下：
1. 文档解析与切分（Chunking）：将长文档切分成大小适中的文本块，一般在 200 到 500 字之间。
2. 向量化（Embedding）：利用向量模型（如 Sentence-Transformer）将每个文本块转换为稠密向量。
3. 向量存储与索引（Vector Store & FAISS）：将向量写入数据库或索引工具，以便于进行相似度搜索。
4. 检索（Retrieval）：用户提问时，将提问向量化，然后在向量库中计算余弦相似度或L2距离，召回最相关的 Top-K 个文本块。
5. 生成（Generation）：将召回的文本块作为“上下文”（Context），连同用户的问题一起拼接成 Prompt 发送给大模型，大模型基于这些准确的参考信息来生成可靠的回答。"""
        
        with open(os.path.join(UPLOAD_FOLDER, "RAG技术综述.txt"), "w", encoding="utf-8") as f:
            f.write(doc2_content)
            
        # 3. 第三章_向量检索.txt
        doc3_content = """向量检索（Vector Search）是实现语义检索和 RAG 框架的底层技术基石。
它的核心任务是：在给定的多维向量集合中，快速找到与目标查询向量距离最近的 K 个向量。
常用的相似度/距离计算方法有：
1. 欧氏距离（L2 Distance）：计算两点之间的绝对几何距离，值越小表示越相似。FAISS的 IndexFlatL2 就是基于该方法。
2. 余弦相似度（Cosine Similarity）：计算两个向量夹角的余弦值，主要衡量向量的方向一致性。
FAISS（Facebook AI Similarity Search）是由 Meta 团队开发的极其高效的向量相似度搜索工具库。它针对 CPU 和 GPU 进行了高度优化，能够支持千万级甚至亿级向量的亚毫秒级检索。
FAISS 提供了多种索引类型，如 Flat（暴力精确搜索）、IVF（倒排文件索引，适用于大规模快速搜索）和 HNSW（分层导航小世界图，检索速度极快且召回率高）。"""
        
        with open(os.path.join(UPLOAD_FOLDER, "第三章_向量检索.txt"), "w", encoding="utf-8") as f:
            f.write(doc3_content)
            
        print("Default course materials successfully generated.")
    
    # Reload and index all files in the folder
    files = [f for f in os.listdir(UPLOAD_FOLDER) if allowed_file(f)]
    for filename in files:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        add_document_to_index(filename, filepath)

# Load static frontend files (if served directly from Flask)
@app.route('/')
def serve_index():
    return send_from_directory('../front', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../front', path)

# ── API ENDPOINTS ──

@app.route('/api/status', methods=['GET'])
def get_status():
    """
    Returns general stats about the retrieval backend
    """
    return jsonify({
        "status": "online",
        "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2",
        "vector_dimension": EMBEDDING_DIM,
        "total_documents": len(documents),
        "total_chunks": len(chunks_metadata)
    })


@app.route('/api/chunks', methods=['GET'])
def get_chunks():
    """
    Returns preview chunks for a specific file.
    Query param: file (filename), limit (default 5)
    """
    filename = request.args.get('file', '')
    limit    = int(request.args.get('limit', 5))

    if not filename:
        return jsonify({"error": "file parameter required"}), 400

    matched = [m["text"] for m in chunks_metadata if m["file"] == filename]
    return jsonify({"file": filename, "chunks": matched[:limit]})

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """
    Returns the list of indexed files with chunk counts and sizes
    """
    result = []
    for name, info in documents.items():
        result.append({
            "name": name,
            "type": info["type"],
            "chunks": info["chunks_count"],
            "size_mb": round(info["size_bytes"] / (1024 * 1024), 2) or 0.01
        })
    return jsonify(result)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Accepts document uploads (PDF/TXT), parses, chunks, embeds, and adds them to FAISS.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    if file and allowed_file(file.filename):
        # 兼容中文的自定义安全文件名清理（标准 secure_filename 会过滤所有中文字符）
        import re
        original_name = file.filename
        clean_name = os.path.basename(original_name)
        clean_name = re.sub(r'[^\w\s\.\-\u4e00-\u9fff]', '', clean_name)
        clean_name = clean_name.replace(' ', '_').strip()
        if not clean_name or clean_name.startswith('.'):
            clean_name = "uploaded_file_" + str(int(time.time())) + clean_name
            
        filename = clean_name
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            chunks_count = add_document_to_index(filename, filepath)
            size_mb = round(os.path.getsize(filepath) / (1024 * 1024), 2) or 0.01
            ext = filename.rsplit('.', 1)[1].lower()
            
            return jsonify({
                "success": True,
                "filename": filename,
                "type": ext,
                "chunks": chunks_count,
                "size_mb": size_mb,
                "total_chunks": len(chunks_metadata),
                "total_docs": len(documents)
            })
        except Exception as e:
            return jsonify({"error": f"Failed to process file: {str(e)}"}), 500
            
    return jsonify({"error": "Invalid file type. Only PDF and TXT are allowed"}), 400

@app.route('/api/query', methods=['POST'])
def query_rag():
    """
    RAG Query endpoint. Receives query, performs FAISS retrieval,
    and returns a generated answer along with Top-K sources.
    """
    data = request.json or {}
    query_text = data.get('query', '').strip()
    top_k = int(data.get('top_k', 3))
    
    if not query_text:
        return jsonify({"error": "Query text is required"}), 400
        
    if not chunks_metadata:
        return jsonify({
            "answer": "知识库当前为空，请先上传一些课程资料文件！",
            "sources": []
        })
        
    try:
        # 1. Embed query
        query_vector = model.encode([query_text])
        query_vector = np.array(query_vector).astype('float32')
        
        # 2. Search FAISS index
        # Search for more than top_k if duplicate filters are needed, but for now simple top_k is fine
        k = min(top_k, len(chunks_metadata))
        distances, indices = index.search(query_vector, k)
        
        # 3. Compile sources
        sources = []
        retrieved_texts = []
        for i, idx in enumerate(indices[0]):
            if idx == -1 or idx >= len(chunks_metadata):
                continue
            meta = chunks_metadata[idx]
            # Convert L2 distance to a standard similarity score (e.g., 1 / (1 + dist))
            # or cosine-like representation for display
            dist = float(distances[0][i])
            score = round(1 / (1 + math.sqrt(dist)), 2)
            
            sources.append({
                "file": meta["file"],
                "score": f"{score:.2f}",
                "text": meta["text"]
            })
            retrieved_texts.append(meta["text"])
            
        # 4. Generate Answer (RAG)
        # Attempt to see if OpenAI/DeepSeek API is configured, otherwise fallback to local high-quality template
        # This guarantees it works offline and provides an incredible online experience if API key is provided
        openai_key = os.getenv("OPENAI_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY")

        if gemini_key:
            try:
                from google import genai
                client = genai.Client(api_key=gemini_key)
                model_name = os.getenv("LLM_MODEL", "gemini-2.0-flash")
                context_str = "\n\n".join([f"[文档 {i+1}]: {txt}" for i, txt in enumerate(retrieved_texts)])
                prompt = f"你是一个智能课程助教。请根据以下参考资料回答用户的问题。\n\n参考资料：\n{context_str}\n\n问题：{query_text}\n\n请用中文写出结构清晰、内容详实的回答。"
                response = client.models.generate_content(model=model_name, contents=prompt)
                answer = response.text
            except Exception as e:
                print(f"Gemini API failed: {e}")
                answer = generate_fallback_answer(query_text, retrieved_texts)

        elif openai_key:
            # We can support calling deepseek/openai dynamically if key is in environment
            # For robustness, we will perform standard OpenAI API call format
            import urllib.request
            import json
            
            api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
            model_name = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
            
            context_str = "\n\n".join([f"[文档 {i+1}]: {txt}" for i, txt in enumerate(retrieved_texts)])
            prompt = f"你是一个智能课程助教。请根据以下参考资料回答用户的问题。如果问题无法从参考资料中得出，你可以结合你的专业背景给出回答，但必须说明参考了外部知识。\n\n参考资料：\n{context_str}\n\n问题：{query_text}\n\n请用中文写出结构清晰、内容详实的回答。"
            
            req_data = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": "你是一个专业的课程知识智能解答助手。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }
            
            try:
                req = urllib.request.Request(
                    f"{api_base}/chat/completions",
                    data=json.dumps(req_data).encode('utf-8'),
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {openai_key}"
                    },
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=15) as response:
                    res_body = json.loads(response.read().decode('utf-8'))
                    answer = res_body["choices"][0]["message"]["content"]
            except Exception as llm_err:
                print(f"LLM API Call failed: {llm_err}. Falling back to rule-based responder.")
                answer = generate_fallback_answer(query_text, retrieved_texts)
        else:
            # High quality local fallback response
            answer = generate_fallback_answer(query_text, retrieved_texts)
            
        return jsonify({
            "answer": answer,
            "sources": sources
        })
        
    except Exception as e:
        return jsonify({"error": f"Retrieval failed: {str(e)}"}), 500

def generate_fallback_answer(query, texts):
    """
    Generates a beautiful, highly structured offline summary answer based on retrieved chunks.
    This guarantees that the user is wowed even when running 100% locally without API keys.
    """
    if not texts:
        return "没有找到与您提问相关的课程资料。请尝试更换关键词提问，或上传更多相关文档。"
        
    intro = f"🌟 **课程知识库检索成功！** 本系统已通过 Sentence-Transformer 与 FAISS 向量检索，为您找到了以下最相关的课程知识要点。以下是为您整理的详细解答：\n\n"
    
    body = ""
    for i, text in enumerate(texts):
        # Format the snippet cleanly
        snippet = text.replace('\n', ' ').strip()
        if len(snippet) > 180:
            snippet = snippet[:180] + "..."
        body += f"🔹 **核心要点 {i+1}：**\n> {snippet}\n\n"
        
    conclusion = "💡 *系统提示：以上内容基于课程本地知识库检索生成。如需接入大语言模型（如 DeepSeek / OpenAI API）生成更连贯自然的合成问答，请在后端 `.env` 文件或系统环境变量中配置相应的 API 密钥。*"
    
    return intro + body + conclusion

if __name__ == '__main__':
    # Initialize index with default files
    initialize_default_documents()
    # Run the server
    print("Starting Flask server on http://127.0.0.1:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
