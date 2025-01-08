// Output today's information
const now = new Date();
const days = [
  "Sunday",
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
];
console.log("\nToday is:");
console.log(`Day: ${days[now.getDay()]}`);
console.log(`Date: ${now.toLocaleDateString()}`);
console.log(`Time: ${now.toLocaleTimeString()}\n`);
