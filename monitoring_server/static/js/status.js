var statuses = {
    Operational: 'badge-success',
    Warning: 'badge-warning',
    Critical: 'badge-danger',
    Unknown: 'badge-warning'
}

var incident_icons = {
    Operational: '<path d="M12 0c-6.627 0-12 5.373-12 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12zm-1.25 16.518l-4.5-4.319 1.396-1.435 3.078 2.937 6.105-6.218 1.421 1.409-7.5 7.626z"/>',
    Warning: '<path fill-rule="evenodd" clip-rule="evenodd" d="M12 0c-6.627 0-12 5.373-12 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12zm6 14h-7v-8h2v6h5v2z"/>',
    Critical: '<path d="M12 0c-6.627 0-12 5.373-12 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12zm-1 5h2v10h-2v-10zm1 14.25c-.69 0-1.25-.56-1.25-1.25s.56-1.25 1.25-1.25 1.25.56 1.25 1.25-.56 1.25-1.25 1.25z"/>',
    Unknown: '<path d="M12 0c-6.627 0-12 5.373-12 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12zm-1 5h2v10h-2v-10zm1 14.25c-.69 0-1.25-.56-1.25-1.25s.56-1.25 1.25-1.25 1.25.56 1.25 1.25-.56 1.25-1.25 1.25z"/>'    
}

var last_info = {}

$(document).ready(function() {
    function fetchServerStatus() {
        $.ajax({
            url: 'api/status',
            method: 'POST',
            dataType: 'json',
            success: function(data) {
                last_info = data
                displayServers();
                createIncidentList();
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error('Ошибка при получении данных:', textStatus, errorThrown);
            }
        });
    }

    function displayServers() {
        const serversContainer = $('#servers');
        serversContainer.empty();

        $.each(last_info.servers, function(serverId, server) {
            const serverItem = `
                <div class="list-group-item" id="${serverId}">
                    <h4 class="list-group-item-heading">
                        ${server.name}
                        <a data-toggle="tooltip" data-placement="bottom" title="Access server services">
                            <i class="fa fa-question-circle"></i>
                        </a>
                    </h4>
                    <p class="list-group-item-text">
                        <span class="badge ${statuses[server.status]}">${server.status}</span>
                    </p>
                    <div class="row ml-0 align-items-center"> 
                        <span class="font-weight-bold mr-2">IP: ${server.ip}</span>
                    </div>
                    <div class="row ml-0 align-items-center"> 
                        <span class="font-weight-bold" style="width: 50px">CPU:</span>
                        <div class="progress bg-dark" style="width: 100%">
                            <div class="progress-bar progress-bar-striped bg-secondary" role="progressbar" style="width: ${server.cpu}%" aria-valuenow="${server.cpu}" aria-valuemin="0" aria-valuemax="100"></div>
                            <span class="position-absolute text-center text-light" style="width:96%">${server.cpu}%</span>
                        </div>
                    </div>
                    <div class="row ml-0 align-items-center"> 
                        <span class="font-weight-bold" style="width: 50px">RAM:</span>
                        <div class="progress bg-dark" style="width: 100%">
                            <div class="progress-bar progress-bar-striped bg-secondary" role="progressbar" style="width: ${server.ram}%" aria-valuenow="${server.ram}" aria-valuemin="0" aria-valuemax="100"></div>
                            <span class="position-absolute text-center text-light" style="width:96%">${server.ram}%</span>
                        </div>
                    </div>
                    <h6 class="font-weight-bold">Services:</h6>
                    <div class="list-group">
                        ${server.services.map(service => `
                            <div class="list-group-item border-light p-0" id="${serverId}.${service.name}">
                                <h5 class="list-group-item-heading font-weight-bold d-flex align-items-center justify-content-between">
                                    <a href="/api/logs/${serverId}.${service.name}" class="pt-1 mx-3 h5">${service.name}</a> <span class="pt-1 badge ${statuses[service.status]} mx-3">${service.status}</a>
                                </h5>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
            serversContainer.append(serverItem);
        });
    }

    function createIncidentList() {
    
        const list = document.createElement('ol');
        list.className = 'list-group';
    
        const updates = last_info.updates;
        const timestamps = Object.keys(updates).sort((a, b) => b - a); 
    
        timestamps.forEach(timestamp => {
            const incidents = updates[timestamp];
            const date = new Date(timestamp * 1000);
            const dateString = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item d-flex align-items-start';
    
            const dateParagraph = document.createElement('p');
            dateParagraph.className = 'font-weight-bold p-0 my-2';
            dateParagraph.textContent = dateString;
            dateParagraph.style.width = '4rem';
    
            const contentDiv = document.createElement('div');
            contentDiv.className = 'ml-3 w-75';
    
            if (Object.keys(incidents).length === 0) {
                const noIncidentsParagraph = document.createElement('p');
                noIncidentsParagraph.className = 'my-2';
                noIncidentsParagraph.textContent = 'Нет событий в этот день.';
                contentDiv.appendChild(noIncidentsParagraph);
            } else {
                const incidentList = document.createElement('ol');
                incidentList.className = 'list-unstyled';
    
                for (const [serverName, incidentsArray] of Object.entries(incidents)) {
                    incidentsArray.forEach(incident => {
                        const incidentItem = document.createElement('li');
                        incidentItem.className = 'mt-2 pb-2'

                        const article = document.createElement('article');
                        article.className = 'd-flex';
    
                        const statusDiv = document.createElement('div');
                        statusDiv.className = 'rounded-circle d-flex justify-content-center border p-1 ' + statuses[incident.severity]
                        statusDiv.style.height = '35px';
                        statusDiv.style.width = '35px';

                        const icon = document.createElement('div');
                        icon.className = 'd-flex justify-content-center';
    
                        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
                        svg.setAttribute('width', '25');
                        svg.setAttribute('height', '25');
                        svg.setAttribute('class', 'text-white');
                        svg.setAttribute('viewBox', '0 0 24 24');
                        svg.setAttribute('fill', 'currentColor');
                        svg.setAttribute('stroke-linejoin', "round")
    
                        svg.innerHTML = incident_icons[incident.severity];
    
                        icon.appendChild(svg);
                        statusDiv.appendChild(icon);
    
                        const textDiv = document.createElement('div');
                        textDiv.style.width = '50vw';

                        const header = document.createElement('div');
                        header.className = 'row ml-2 align-items-center justify-content-between';

                        const title = document.createElement('h5');
                        title.className = 'font-weight-bold w-100 my-0 pt-1';
                        title.textContent = incident.title;

                        const time = document.createElement('time');
                        const timeString = new Date(incident.timestamp * 1000).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
                        time.setAttribute('time', new Date(incident.timestamp * 1000).toISOString());
                        time.className = 'small text-muted ml-3 pt-2';
                        time.textContent = timeString;

                        const description = document.createElement('span');
                        description.style.width = '30vw'
                        description.className = 'ml-2 d-flex';
                        description.innerHTML = incident.text.replace('\n', '<br>');
    
                        header.appendChild(title);
                        header.appendChild(time);
                        textDiv.appendChild(header);
                        textDiv.appendChild(description);
                        article.appendChild(statusDiv);
                        article.appendChild(textDiv);
                        incidentItem.appendChild(article);
                        incidentList.appendChild(incidentItem);
                    });
                }
                contentDiv.appendChild(incidentList);
            }
    
            listItem.appendChild(dateParagraph);
            listItem.appendChild(contentDiv);
            list.appendChild(listItem);
        });
    
        $('#updates').empty();
        const updates_header = document.createElement('h4')
        updates_header.className = "card-header text-center font-weight-bold"
        updates_header.innerText = "События за последние 7 дней"
        $('#updates').append(updates_header)
        $('#updates').append(list);
    }

    fetchServerStatus();
    var intervalId = window.setInterval(function(){
        fetchServerStatus();
      }, 10000);
    
});
