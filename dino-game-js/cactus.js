class Cactus {
    shape;
    position;
  
    constructor({ w, h, x }) {
      this.position = vector(x, 0);
      this.shape = rect(this.position, vector(w, h));
    }
  }
  
  const spawnCactus = ({ wMin, wMax, hMin, hMax, dMin, dMax }) => (cactuses) => {
    const prevX = cactuses.length > 0 ? cactuses[cactuses.length - 1].position[0] : 0;
  
    return new Cactus({
      w: randomInt(wMin, wMax),
      h: randomInt(hMin, hMax),
      x: prevX + randomInt(dMin, dMax),
    });
  }
  
  const renderCactus = (context) => (cactus) => {
    context.beginPath();
    
    context.rect(
      -cactus.shape.size[0] / 2, 0, 
      cactus.shape.size[0], -cactus.shape.size[1]
    );
  
    context.arc(0, 0, cactus.shape.r, 0, Math.PI * 2);
    context.stroke();
    }