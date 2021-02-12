function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
// TODO: 1000 steps for 6500 scroll height
// Implement for greater scroll height
async function demo() {
  var scrollHeight = document.body.scrollHeight;
  console.log(`TOTAL HEIGHT: ${scrollHeight}`);

  for (let step = 0; step <= 1000; step += 100) {
    console.log(`SCROLLED AMOUNT: ${step}`);
    window.scrollBy(0, step);
    await sleep(1000);
  }
}

demo();
