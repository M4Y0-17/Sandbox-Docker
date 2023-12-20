function updateTimers() {
    const timers = document.querySelectorAll('[id^="timer-"]');
    timers.forEach(timer => {
        let expirationTimeInSeconds = parseInt(timer.dataset.expirationTime);
        if (expirationTimeInSeconds > 0) {
            expirationTimeInSeconds--;
            timer.dataset.expirationTime = expirationTimeInSeconds.toString();
            const hours = Math.floor(expirationTimeInSeconds / 3600);
            const minutes = Math.floor((expirationTimeInSeconds % 3600) / 60);
            const seconds = expirationTimeInSeconds % 60;
            timer.textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        } else {
            timer.textContent = "00:00:00";
        }
    });
}

setInterval(updateTimers, 1000);

function searchTable() {
    var input, filter, table, tr, td, i, txtValue;
    var filterType = document.getElementById("filterType").value;
    input = document.getElementById("searchBox");
    filter = input.value.toUpperCase();
    table = document.getElementById("dockerTable");
    tr = table.getElementsByTagName("tr");
    for (i = 1; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td")[filterType];
        if (td) {
            txtValue = td.textContent || td.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}
