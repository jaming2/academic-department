let currentProblem = null;

function openProblem(problemNumber) {
    currentProblem = problemNumber;

    document.getElementById('editor-area').style.display = 'block';
    document.getElementById('problem-title').innerText = `${problemNumber}번 문제`;
}

async function submitCode() {
    const code = document.getElementById('code-input').value;

    const response = await fetch('/submit_problem', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            problem: currentProblem,
            code: code
        })
    });

    const data = await response.json();

    const resultDiv = document.getElementById('result');

    if (data.success) {
        resultDiv.innerHTML = '<span style="color:green">성공!</span>';
        setTimeout(() => {
            location.reload();
        }, 1000);
    } else {
        resultDiv.innerHTML = `
            <span style="color:red">실패</span><br>
            출력값: ${data.output || ''}<br>
            에러: ${data.error || ''}
        `;
    }
}

async function goStudy() {
    const response = await fetch('/check_login');

    const data = await response.json();

    if (!data.logged_in) {
        alert('로그인을 먼저 해주세요.');
        return;
    }

    location.href = '/study';
}
