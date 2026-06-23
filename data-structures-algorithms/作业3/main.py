html = input()
stack = []
is_good = True
i = 0

while i < len(html):
    if html[i] == '<':
        #Check if this is a closing tag (</tag>)
        if i + 1 < len(html) and html[i + 1] == '/':
            
            j = html.find('>', i)
            if j == -1:  # No closing '>'
                is_good = False
                break
            tag = html[i + 2 : j]  # Tag name (without '</' and '>')
            
            #Check if the closing tag matches the last opening tag
            if not stack or stack.pop() != tag:
                is_good = False
                break
            i = j + 1  
        
        else:
            #Opening tag (<tag>)
            j = html.find('>', i)
            if j == -1:
                is_good = False
                break
            tag = html[i + 1 : j].split()[0]#Take the first word (ignore attributes)
            stack.append(tag)
            i = j + 1
    else:
        i += 1  

print("YES" if is_good and not stack else "NO")