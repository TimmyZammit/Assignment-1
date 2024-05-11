document.getElementById('triggerFunction').addEventListener('click', async () => {
    const numberOfCalls = 10000;
    for (let i = 0; i < numberOfCalls; i++) {
        fetch('https://europe-west1-assignment-1-v2.cloudfunctions.net/generateRandNum')
            .then(response => response.text())
            .then(data => console.log(`Response from function ${i}: ${data}`))
            .catch(error => console.error('Error calling function:', error));
    }
});
