document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileSelectLink = document.getElementById('file-select-link');
    const addFilesButton = document.getElementById('add-files-button');
    const timelineContainer = document.getElementById('timeline');
    const statusContainer = document.getElementById('status');
    const dragOverlay = document.getElementById('drag-overlay');
    const timeTooltip = document.getElementById('time-tooltip');

    // --- State ---
    let timeline = null;
    let timelineItems = new vis.DataSet();
    let timelineGroups = new vis.DataSet();
    let fileMetas = {};
    let isInitialState = true;

    // --- Event Listeners ---
    window.addEventListener('dragenter', (e) => { e.preventDefault(); dragOverlay.style.display = 'flex'; });
    window.addEventListener('dragleave', (e) => { if (e.relatedTarget === null) dragOverlay.style.display = 'none'; });
    window.addEventListener('dragover', (e) => e.preventDefault());
    window.addEventListener('drop', (e) => {
        e.preventDefault();
        dragOverlay.style.display = 'none';
        handleFiles(e.dataTransfer.files);
    });

    dropZone.addEventListener('click', () => fileInput.click());
    addFilesButton.addEventListener('click', () => fileInput.click());
    fileSelectLink.addEventListener('click', (e) => e.preventDefault());
    fileInput.addEventListener('change', () => {
        handleFiles(fileInput.files);
        fileInput.value = '';
    });

    timelineContainer.addEventListener('click', (event) => {
        if (event.target.classList.contains('delete-btn')) {
            const filename = event.target.dataset.filename;
            if (filename && fileMetas[filename]) {
                delete fileMetas[filename];
                updateTimeline();
            }
        }
    });

    // --- Core Functions ---
    function handleFiles(files) {
        statusContainer.innerHTML = `Uploading and processing ${files.length} file(s)...`;
        for (const file of files) {
            if (fileMetas[file.name]) {
                statusContainer.innerHTML += `<br>Skipping already processed file: ${file.name}`;
                continue;
            }
            uploadFile(file);
        }
    }

    function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        fetch('http://127.0.0.1:5000/process', { method: 'POST', body: formData })
        .then(response => response.json())
        .then(data => {
            if (data.error) throw new Error(data.error);
            fileMetas[data.name] = data;
            updateTimeline();
        })
        .catch(error => {
            console.error('Error:', error);
            statusContainer.innerHTML += `<br><b>Error processing ${file.name}:</b> ${error.message}`;
        });
    }

    function millisToHMS(ms, includeMillis = false) {
        if (isNaN(ms) || ms < 0) return "00:00:00";
        const totalSeconds = ms / 1000;
        const h = Math.floor(totalSeconds / 3600).toString().padStart(2, '0');
        const m = Math.floor((totalSeconds % 3600) / 60).toString().padStart(2, '0');
        const s = Math.floor(totalSeconds % 60).toString().padStart(2, '0');
        if (includeMillis) {
            const millis = (ms % 1000).toString().padStart(3, '0');
            return `${h}:${m}:${s}.${millis}`;
        }
        return `${h}:${m}:${s}`;
    }

    function updateTimeline() {
        const allFiles = Object.values(fileMetas);
        
        if (isInitialState && allFiles.length > 0) {
            isInitialState = false;
            dropZone.style.display = 'none';
            addFilesButton.style.display = 'block';
        }

        statusContainer.innerHTML = allFiles.length > 0 ? `<strong>Timeline Updated</strong>: ${allFiles.length} file(s) loaded.` : 'Ready. Drag files or click to upload.';

        timelineGroups.clear();
        timelineItems.clear();

        allFiles.forEach((file) => {
            const startStr = millisToHMS(file.startTime);
            const endStr = millisToHMS(file.endTime);
            const groupContent = document.createElement('div');
            groupContent.className = 'vis-group-content';
            const groupName = document.createElement('span');
            groupName.textContent = file.name;
            groupContent.appendChild(groupName);
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'delete-btn';
            deleteBtn.title = 'Remove';
            deleteBtn.innerHTML = '&times;';
            deleteBtn.dataset.filename = file.name;
            groupContent.appendChild(deleteBtn);
            timelineGroups.add({ id: file.name, content: groupContent });
            timelineItems.add({
                id: file.name,
                group: file.name,
                content: `${((file.endTime - file.startTime) / 1000).toFixed(0)}s`,
                start: new Date(file.startTime),
                end: new Date(file.endTime),
                type: 'range',
                title: `Start: ${startStr}<br>End: ${endStr}`,
                className: file.name.toLowerCase().endsWith('.tc') ? 'tc-range' : 'video-range'
            });
        });

        if (!timeline && allFiles.length > 0) {
            const options = {
                stack: false,
                minHeight: '250px',
                showCurrentTime: true,
                zoomMin: 1000,
                moment: (date) => vis.moment(date).utc(),
                format: {
                    minorLabels: { second: 'HH:mm:ss', minute: 'HH:mm:ss', hour: 'HH:mm:ss' },
                    majorLabels: { second: 'HH:mm', minute: 'HH:mm', hour: 'HH:mm' }
                },
                snap: function (date) {
                    const time = date.getTime();
                    let snappedTime = time;
                    const snapDistance = 500; // Snap within 500ms
                    let minDistance = Infinity;
                    let closestItemTime = null;

                    timelineItems.forEach(item => {
                        const itemData = fileMetas[item.id];
                        if (!itemData) return;
                        [itemData.startTime, itemData.endTime].forEach(itemTime => {
                            const dist = Math.abs(time - itemTime);
                            if (dist < minDistance) {
                                minDistance = dist;
                                closestItemTime = itemTime;
                            }
                        });
                    });

                    if (closestItemTime !== null && minDistance < snapDistance) {
                        snappedTime = closestItemTime;
                    }
                    return new Date(snappedTime);
                }
            };
            timeline = new vis.Timeline(timelineContainer, timelineItems, timelineGroups, options);
            // Add a custom time bar for the hover effect
            timeline.addCustomTime(new Date(0), 'hover-line');

            timeline.on('mouseMove', (properties) => {
                const time = properties.time.getTime();
                // Always move the vertical line
                timeline.setCustomTime(new Date(time), 'hover-line');

                if (properties.item !== null) {
                    // If the mouse is over an item, hide our custom tooltip 
                    // and let the library show the item's own title.
                    timeTooltip.style.display = 'none';
                } else {
                    // If the mouse is over the timeline background, show our custom tooltip.
                    timeTooltip.style.display = 'block';
                    timeTooltip.style.left = (properties.event.pageX + 15) + 'px';
                    timeTooltip.style.top = (properties.event.pageY - 10) + 'px';
                    timeTooltip.innerHTML = millisToHMS(time, true);
                }
            });

            // Hide the tooltip when the mouse leaves the container
            timelineContainer.addEventListener('mouseleave', () => {
                timeTooltip.style.display = 'none';
            });

        } else if (timeline) {
            timeline.setGroups(timelineGroups);
            timeline.setItems(timelineItems);
            if (allFiles.length > 0) timeline.fit();
        }
    }
});
