const vector = (x, y) => [x, y];

const length = v => Math.sqrt(v[0] * v[0] + v[1] * v[1]);
// lengthSquare

const add = (a, b) => [a[0] + b[0], a[1] + b[1]];
const inverse = (a) => [-a[0], -a[1]];
const substract = (a, b) => add(a, inverse(b));
const scale = (a, s) => [a[0] * s, a[1] * s];


const circle = (x, y, r) => ({
  o: vector(x, y),
  r
});

// const rect = (x1, y1, x2, y2) => [
//   vector(x1, y1), // левый нижний
//   vector(x2, y2), // правый верхний
// ];

const rect = (o, size) => ({
  o,
  size,
});



const collideCircles = (a, b) => a.r + b.r >= length(substract(a.o, b.o));

const collideRectangles = (a, b) => {

  let xs = [
    a.o[0] - a.size[0] / 2,
    a.o[0] + a.size[0] / 2,
    b.o[0] - b.size[0] / 2,
    b.o[0] + b.size[0] / 2
  ];

  let ys = [
    a.o[1],
    a.o[1] + a.size[1],
    b.o[1],
    b.o[1] + b.size[1]
  ];
  // console.log(ys);

  return [xs, ys].every(([al, ar, bl, br]) => {

    if (al <= bl) {
      if (ar >= bl) {
        return true;
      }
    } else {
      if(br >= al) {
        return true;
      }
    }
  });

}