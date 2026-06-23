class Dino {
    shape;
    position;
  
    v;
  
    // vx = 10;
    // vy = 0;
  
    g;
    jumpAcceleration;
    // vy0 = 100;
  
    sprite;
    spriteIsReady = false;
    spriteW;
    spriteH;
  
    constructor({ h, w, vx, g , vy0 }) {
      this.position = [0, 0];
      this.shape = rect(this.position, vector(w, h));
      this.v = vector(vx, 0);
      this.g = vector(0, -g);
      this.jumpAcceleration = vector(0, vy0);
  
  
      this.sprite = new Image();
      this.sprite.src = "./pngegg.png";
      this.sprite.onload = (event) => {
        console.log(event);
        this.spriteIsReady = true;
        this.spriteW = this.sprite.width;
        this.spriteH = this.sprite.height;
  
        const h = this.shape.size[0] * this.spriteH / this.spriteW;
  
        this.shape = rect(this.shape.position, vector(this.shape.size[0], h));
      }
  
    }
  
    jump() {
      if (this.position[1] === 0) {
        this.v = add(this.v, this.jumpAcceleration);
      }
    }
  
    step(dt) {
      this.v = add(this.v, scale(this.g, dt));
      this.position = add(this.position, scale(this.v, dt));
  
      // Столкновение с землей
      if (this.position[1] <= 0) {
        this.v = vector(this.v[0], 0);
        this.position = vector(this.position[0], 0);
      }
  
      // let r = this.shape.r;
      this.shape = rect(this.position, this.shape.size);
    }
  
  }
  
  
  /**
   * @param {CanvasRenderingContext2D} context
   */
  renderDino = (context) => (dino) => {
    context.beginPath();
  
    // context.drawImage()
    // context.rect(
    //   -dino.shape.size[0] / 2, 0, 
    //   dino.shape.size[0], -dino.shape.size[1]
    // );
  
    if (dino.spriteIsReady) {
      context.drawImage(
        dino.sprite, 
        110, 100,
        dino.spriteW - 110 - 120,
        dino.spriteH - 100 - 100,
        -dino.shape.size[0] / 2, 
        -dino.shape.size[1], 
        dino.shape.size[0], 
        dino.shape.size[1]
    );
    }
  
    // context.arc(0, 0, dino.shape.r, 0, Math.PI * 2);
    context.stroke();
  }