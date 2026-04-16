const express = require('express');
const { Task } = require('../models/task');

const router = express.Router();

router.get('/', async (_req, res) => {
  const tasks = await Task.find().sort({ createdAt: -1 });
  res.json(tasks);
});

router.post('/', async (req, res) => {
  const { title, description } = req.body;
  const task = await Task.create({ title, description, done: false });
  res.status(201).json(task);
});

router.patch('/:id', async (req, res) => {
  const updated = await Task.findByIdAndUpdate(req.params.id, req.body, { new: true });
  res.json(updated);
});

router.delete('/:id', async (req, res) => {
  await Task.findByIdAndDelete(req.params.id);
  res.status(204).send();
});

module.exports = { router };
