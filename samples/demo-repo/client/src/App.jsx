import React, { useEffect, useState } from 'react';
import { TaskList } from './components/TaskList';

export default function App() {
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    fetch('/tasks').then((r) => r.json()).then(setTasks);
  }, []);

  return (
    <main>
      <h1>TaskForge</h1>
      <TaskList tasks={tasks} />
    </main>
  );
}
