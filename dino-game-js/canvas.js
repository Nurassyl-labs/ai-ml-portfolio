const bars = (context) => (data) => {
    context.beginPath();
    data.forEach(number => {
      context.rect(0, 0, 1, number);
      context.translate(1.5, 0);
    });
  }; 
  
  const doublebars = (context) => (data) => {
    context.beginPath();
    data.forEach(number => {
  
      // context.translate(0, number);
      context.rect(0, number, 1, number / 2);
      
      context.translate(1.5, 0);
    });
  }; 
  
  
  const draw = (canvas) => {
  
    const width = canvas.offsetWidth;
    const height = canvas.offsetHeight;
  
    const data = [10, 20, 40, 20, 60];
  
  
  
    /**
     * @type {CanvasRenderingContext2D}
     */
    const context = canvas.getContext("2d"); // webgl webgl2
    
    
    context.fillStyle = "hsl(50, 100.00%, 87.80%)";
    const a = Math.PI / 6;
    context.translate(600, 500);
    context.scale(50, 50);
    context.rotate(a);
  
    context.moveTo(0, 0);
    context.lineTo(1, 0);
    context.arc(0, 0, 1, 0, Math.PI / 2);
    context.closePath();
  
    context.lineWidth = 4 / 50;
    context.stroke();
  
  
    context.clearRect(0, 0, width, height);
  
    // const barWidth = 50;
    // const barHeight = 10;
    // const barSpace = 25;
  
    context.save();
    context.translate(100, 700);
    context.scale(50, -10);
  
    context.save();
    bars(context)(data);
    context.fillStyle = "hsl(50, 50%, 50%)";
    context.fill();
    context.restore();
  
    context.save();
    doublebars(context)(data);
    context.fillStyle = "hsl(100, 50%, 50%)";
    context.fill();
    context.restore();
  
    context.restore();
    
  
    context.save();
    context.translate(600, 700);
    context.scale(20, -20);
  
    bars(context)(data);
    context.fillStyle = "hsl(120, 50%, 50%)";
    context.fill();
    
    context.restore();
    
  
    context.rotate(Math.PI / 4); // 45 градусов
    context.translate(100, 100);
  
    context.fillStyle = "hsl(50, 50%, 50%)";
    data.forEach((number, index) => {
      // const x = (barWidth + barSpace) * index;
      
      context.fillRect(0, 0, barWidth, barHeight * number)
      
      context.translate(barWidth + barSpace, 0);
    });
  
  
    context.fillStyle = "hsl(120, 8.80%, 51.00%)";
  
    context.fillRect(20, 20, 100, 100)
  
    context.fillStyle = "hsl(220, 50%, 50%)";
    
    context.fillRect(100, 100, 100, 100);
    // context.beginPath();
    // context.rect();
    // context.fill();
  
    context.strokeRect(100, 100, 100, 100);
  
  
    context.beginPath();
    context.moveTo(300, 300);
    context.lineTo(400, 400);
    context.lineTo(400, 300);
    // context.closePath();
    
    context.fillStyle = "hsl(50, 50%, 50%)";
    context.fill();
    context.strokeStyle = "hsl(0, 0%, 0%)";
    context.lineWidth = 4;
    context.stroke();
  
    
    context.beginPath();
    context.moveTo(400, 300);
    context.lineTo(400, 200);
    context.lineTo(300, 300);
    context.closePath();
    
    context.fillStyle = "hsla(50, 50%, 50%, 0.5)";
    context.fill();
    context.stroke();
  
  
    console.log(context);
  
  }