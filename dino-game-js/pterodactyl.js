class Pterodactyl {
    shape;
    position;
    v;
  
    
    
    constructor({ w, h, x, y, vx}) {
      this.position = vector(x, y);
      this.shape = rect(this.position, vector(w, h));
      this.v = vector(-vx, 0);
      console.log(vx);
  
    }
  
    step(dt) {
      this.position = add(this.position, scale(this.v, dt));
      this.shape = rect(this.position, this.shape.size);
    }
  }
  
  const spawnPterodactyl = ({ wMin, wMax, hMin, hMax, dMin, dMax, vMin, vMax, yMin, yMax }) => (peterodactyls) => {
    const prevX = peterodactyls.length > 0 ? peterodactyls[peterodactyls.length - 1].position[0] : 0;
  
  
    return new Pterodactyl({
      w: randomInt(wMin, wMax),
      h: randomInt(hMin, hMax),
      x: prevX + randomInt(dMin, dMax),
      y: randomInt(yMin, yMax),
      vx: randomInt(vMin, vMax),
    });
  }
  
  const renderPterodactyl= (context) => (peterodactyl) => {
    context.beginPath();
    
    context.rect(
      -peterodactyl.shape.size[0] / 2, 0, 
      peterodactyl.shape.size[0], -peterodactyl.shape.size[1]
    );
  
    // context.arc(0, 0, cactus.shape.r, 0, Math.PI * 2);
    context.stroke();
  }