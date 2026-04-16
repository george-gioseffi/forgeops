// Quick seed script: inserts a few tasks so the UI isn't empty.
const mongoose = require('mongoose');
const { Task } = require('../server/models/task');

async function main() {
  await mongoose.connect(process.env.MONGO_URL || 'mongodb://localhost:27017/taskforge');
  await Task.create([
    { title: 'Write README', description: 'The real one.', done: false },
    { title: 'Add tests', description: 'There are none.', done: false },
    { title: 'Deploy somewhere', description: '', done: false },
  ]);
  await mongoose.disconnect();
}

main().catch((e) => { console.error(e); process.exit(1); });
