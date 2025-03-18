document.addEventListener('DOMContentLoaded', function() {
  // Sample records for testing
  const sampleRecords = [
    {
      id: 1,
      title: "Urgent Bug Fix",
      priority: "high",
      status: "pending",
      tags: ["urgent", "bug"]
    },
    {
      id: 2,
      title: "Documentation Update",
      priority: "low",
      status: "completed",
      tags: ["documentation"]
    },
    {
      id: 3,
      title: "Security Patch",
      priority: "high",
      status: "in_progress",
      tags: ["important", "security"]
    }
  ];

  // Elements
  const textFilter = document.getElementById('textFilter');
  const testText = document.getElementById('testText');
  const textResult = document.getElementById('textResult');
  const recordFilter = document.getElementById('recordFilter');
  const recordsTable = document.getElementById('recordsTable');

  // Event listeners
  textFilter.addEventListener('input', evaluateTextFilter);
  testText.addEventListener('input', evaluateTextFilter);
  recordFilter.addEventListener('input', evaluateRecordFilter);

  // Initial evaluation
  evaluateTextFilter();
  evaluateRecordFilter();

  function evaluateTextFilter() {
    const filter = textFilter.value.trim();
    const text = testText.value.trim();

    if(!filter || !text) {
      textResult.textContent = 'undefined';
      textResult.className = 'badge bg-secondary';
      return;
    }

    fetch('/ajax', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        mode: 'text',
        filter: filter,
        input: text
      })
    })
    .then(response => response.json())
    .then(data => {
      textResult.textContent = data.result ? 'SUCCESS' : 'FAIL';
      textResult.className = `badge ${data.result ? 'bg-success' : 'bg-danger'}`;
    })
    .catch(error => {
      textResult.textContent = 'Error';
      textResult.className = 'badge bg-warning';
      console.error('Error:', error);
    });
  }

  function evaluateRecordFilter() {
    const filter = recordFilter.value.trim();

    if(!filter) {
      updateRecordsTable(sampleRecords.map(r => ({ ...r, result: false })));
      return;
    }

    fetch('/ajax', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        mode: 'records',
        filter: filter,
        records: sampleRecords
      })
    })
    .then(response => response.json())
    .then(data => {
      updateRecordsTable(data.results);
    })
    .catch(error => {
      console.error('Error:', error);
      recordsTable.innerHTML = '<tr><td colspan="6" class="text-danger">Error evaluating filter</td></tr>';
    });
  }

  function updateRecordsTable(records) {
    recordsTable.innerHTML = records.map(record => `
      <tr>
        <td>${record.id}</td>
        <td>${record.title}</td>
        <td>${record.priority}</td>
        <td>${record.status}</td>
        <td>${record.tags.join(', ')}</td>
        <td>
          <span class="badge ${record.result ? 'bg-success' : 'bg-danger'}">
            ${record.result ? 'SUCCESS' : 'FAIL'}
          </span>
        </td>
      </tr>
    `).join('');
  }
});