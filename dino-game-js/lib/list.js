const randomInt = (min, max) => 
  min + Math.floor(Math.random() * (max - min));


const createArray = (mapFunction = index => index) => length => 
  Array.from({ length }, (_, index) => mapFunction(index));


// debounce
// "накапливаем события" пока они не перестанут проиходить в течении N ms
const debounce = func => delay => {
  let timerId = null;

  return (...args) => {
    if (timerId === null) {
      func(...args);
    }

    clearTimeout(timerId);
    timerId = setTimeout(() => {
      func(...args)
      timerId = null;
    }, delay);
  }
}


// throttle
// Выполнять обработчик не чаще чем раз в N ms
const throttle = func => delay => {
  let timerId = null;

  return (...args) => {
    if (timerId === null) {
      // func(...args);
      timerId = setTimeout(() => {
        timerId = null;
        func(...args);
      }, delay);
    }
  };
}