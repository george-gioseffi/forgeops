const mongoose = require('mongoose');

const TaskSchema = new mongoose.Schema({
  title: { type: String, required: true },
  description: { type: String, default: '' },
  done: { type: Boolean, default: false },
}, { timestamps: true });

exports.Task = mongoose.model('Task', TaskSchema);
