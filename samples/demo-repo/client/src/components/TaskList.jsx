import React from 'react';

export function TaskList({ tasks }) {
  if (!tasks || tasks.length === 0) {
    return <p>No tasks yet.</p>;
  }
  return (
    <ul>
      {tasks.map((t) => (
        <li key={t._id}>{t.title}</li>
      ))}
    </ul>
  );
}
