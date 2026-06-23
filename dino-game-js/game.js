class Game {

    dino = null;
    futureCactuses = [];
    pastCactuses = [];
    
    futurePterodactyls = [];
    pastPterodactyls = [];
    
  
  
    gameIsOver = false;
    gameIsPaused = false;
    startTime = 0;
    lastFrameTime = 0;
    
    score = 0;
  
    width;
    height;
  
    horizon;
    middle;
  
    speed;
  
  
    constructor(canvas) {
  
      const context = canvas.getContext("2d");
    
      // Render
      this.width = context.canvas.offsetWidth;
      this.height = context.canvas.offsetHeight;
  
      this.horizon = this.height / 2;
      this.middle = this.width / 2;
  
      this.dino = new Dino({
        h: 100,
        w: 60,
        vx: 400,
        g: 3000,
        vy0: 1000,
      });
    
      this.spawnCactus = spawnCactus({ 
        wMin: 40, wMax: 50, 
        hMin: 40, hMax: 80, 
        dMin: 400, dMax: 500 
      });
  
      this.spawnPterodactyl = spawnPterodactyl({ 
        wMin: 100, wMax: 120, 
        hMin: 20, hMax: 30, 
        dMin: 2000, dMax: 3000,
        yMin: 150, yMax: 300,
        vMin: 200, vMax: 200,
      });
  
      for (let index = 0; index < 2; index++) {
        this.futureCactuses.push(this.spawnCactus(this.futureCactuses));
      }
    
      for (let index = 0; index < 3; index++) {
        this.futurePterodactyls.push(this.spawnPterodactyl(this.futurePterodactyls));
      }
  
      window.addEventListener("keydown", (event) => {
        if (event.code === "Space") {
          if (this.gameIsPaused) {
            this.gameIsPaused = false;
          } else {
            this.dino.jump();
            event.preventDefault();
          }
  
        }
      });
  
      window.addEventListener("blur", () => {
        this.gameIsPaused = true;
      })
  
      this.render = this.render_(context);
    }
  
    start() {
      this.speed = 0.8;
      this.gameIsOver = false;
      this.gameIsPaused = false;
      this.startTime = Date.now();
      this.lastFrameTime = Date.now();
      this.doFrame(); // 60 fps
    }
  
    
    /**
     * @param {CanvasRenderingContext2D} context
     */
    doFrame = () => {
      let now = Date.now();
      let dt = (now - this.lastFrameTime) / 1000;
      this.lastFrameTime = now;
  
      if (!this.gameIsOver && !this.gameIsPaused) {
        this.progress(dt);
      }
  
      this.render();
  
      requestAnimationFrame(this.doFrame);
    }
  
    progress = dt => {
  
      dt = dt * this.speed;
  
      this.dino.step(dt);
  
      [
        ...this.pastPterodactyls, 
        ...this.futurePterodactyls,
      ].forEach(pterodactyl => pterodactyl.step(dt));
  
  
      [
        ...this.futureCactuses,
        ...this.futurePterodactyls,
      ].forEach(cactus => {
        if (collideRectangles(this.dino.shape, cactus.shape)) {
          this.gameIsOver = true;
          console.log("game over");
          console.log(this.score)
        }
      });
  
      
      const dinoLeft = this.dino.shape.o[0] - this.dino.shape.size[0] / 2;
      while (true) {
        let cactus = this.futureCactuses[0];
        if (!cactus || (dinoLeft < cactus.shape.o[0] + cactus.shape.size[0] / 2)) {
          break;
        }
        
        this.score += 1;
        this.pastCactuses.push(this.futureCactuses.shift());
        if (this.pastCactuses.length > 10) {
          this.pastCactuses.shift();
        }
  
        this.futureCactuses.push(this.spawnCactus(this.futureCactuses));
      }
  
      while (true) {
        let pterodactyl = this.futurePterodactyls[0];
        if (!pterodactyl || (dinoLeft < pterodactyl.shape.o[0] + pterodactyl.shape.size[0] / 2)) {
          break;
        }
        
        this.score += 1;
        this.pastPterodactyls.push(this.futurePterodactyls.shift());
        if (this.pastPterodactyls.length > 10) {
          this.pastPterodactyls.shift();
        }
        
        this.futurePterodactyls.push(this.spawnPterodactyl(this.futurePterodactyls));
      }
  
      this.speed = 0.8 + Math.floor(this.score / 5) * 0.1;
    }
  
    /**
     * @param {CanvasRenderingContext2D} context
     */
    render_ = context => () => {
  
      const [x, y] = this.dino.position;
  
      context.clearRect(0, 0, this.width, this.height);
      
      context.save();
      context.translate(0, this.horizon);
  
      context.beginPath();
      context.moveTo(0, 0);
      context.lineTo(this.width, 0);
      context.stroke();
      
      context.translate(this.middle - x, 0);
  
  
      context.save();
      context.translate(x, -y);
      renderDino(context) (this.dino);
      context.restore();
  
      // console.log([...pastCactuses, ...futureCactuses]);
      [ 
        ...this.pastCactuses, 
        ...this.futureCactuses,
      ].forEach(cactus => {
        context.save();
        
        const [cx, cy] = cactus.position;
        context.translate(cx, -cy);
        renderCactus(context) (cactus);
        context.restore();
      });
  
      [
        ...this.pastPterodactyls, 
        ...this.futurePterodactyls,
      ].forEach(pterodactyl => {
        context.save();
        
        const [cx, cy] = pterodactyl.position;
        context.translate(cx, -cy);
        renderPterodactyl(context) (pterodactyl);
        context.restore();
      });
  
      // x += 1 * dt;
  
  
      context.restore();
  
      context.font = "800 24px monospace";
      context.textBaseline = "top";
      
      context.save();
      context.translate(this.width, 0);
      // context.scale(2, 2);
      context.textAlign = "right";
      context.fillText(this.score, -10, 10);
      context.restore();
  
      
      if (this.gameIsOver) {
        context.save();
        context.translate(this.middle, 0);
        // context.scale(2, 2);
        context.textAlign = "center";
        context.fillText("End", 0, 10);
        context.fillText("score:" + this.score, 0, 50);
        context.restore();
      } else if (this.gameIsPaused) {
        context.save();
        context.translate(this.middle, 0);
        // context.scale(2, 2);
        context.textAlign = "center";
        context.fillText("pouse", 0, 10);
        context.restore();
      }
    }
  
  }