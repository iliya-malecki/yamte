let state = {
    history: [],
    mousedown: false,
    pathidx: 0
}

function update_history(e) {
    state.history.push({
        x: e.pageX,
        y: e.pageY,
        t: Date.now(),
        mousedown: state.mousedown,
        pathidx: state.pathidx,
        reason: e.type
    })
}

document.addEventListener('mousemove', update_history);
document.addEventListener('scroll', update_history);
document.addEventListener('mousedown', ()=>{
    state.mousedown=true
});
document.addEventListener('mouseup', ()=>{
    state.mousedown=false
    state.pathidx++
});

function exportJson(el) {

    var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(
        JSON.stringify({
            'data': state.history,
            'useragent': window.navigator.userAgent
        })
    );

    const link = document.createElement('a')
    link.href = dataStr
    link.download = 'mousedata.json'
    document.body.appendChild(link)
    link.click()

    document.body.removeChild(link)
    window.URL.revokeObjectURL(dataStr)
}
