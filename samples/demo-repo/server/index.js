const express = require('express');
const mongoose = require('mongoose');
const { router } = require('./routes/tasks');

const PORT = process.env.PORT || 4000;
const MONGO_URL = process.env.MONGO_URL || 'mongodb://localhost:27017/taskforge';

const app = express();
app.use(express.json());
app.use('/tasks', router);

mongoose.connect(MONGO_URL).then(() => {
  app.listen(PORT, () => console.log(`taskforge listening on :${PORT}`));
}).catch((err) => {
  console.error('mongo error', err);
  process.exit(1);
});
