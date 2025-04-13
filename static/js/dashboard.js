function selectLog(selectObj) {
    const value = selectObj.value.trim();
    const url = new URL(window.location.href);
    const params = url.searchParams;

    value ? params.set("log", value) : params.delete("log");
    url.search = params.toString();
    window.location.href = url.toString();
}

function gotoNextPage(){
    actualPage = parseInt(document.getElementById("actualPage").innerText);
    actualPage += 1;
    console.log("actualPage", actualPage);
    const url = new URL(window.location.href);
    const params = url.searchParams;
    params.set("page", actualPage);
    url.search = params.toString();
    window.location.href = url.toString();
}

function gotoPrevPage(){
    actualPage = parseInt(document.getElementById("actualPage").innerText);
    actualPage -= 1;
    console.log("actualPage", actualPage);
    const url = new URL(window.location.href);
    const params = url.searchParams;
    params.set("page", actualPage);
    url.search = params.toString();
    window.location.href = url.toString();
}

function applyFilter(){
    const url = new URL(window.location.href);
    const params = url.searchParams;

    const typesSelect = document.getElementById("typesSelect");
    const selectedOptions = [...typesSelect.selectedOptions].map(o => o.value.trim());
    if(selectedOptions.length > 0){
        params.set("types", selectedOptions);
    } else {
        params.delete("types");
    }

    const functionNameInput = document.getElementById("functionNameInput").value.trim();
    functionNameInput ? params.set("function_name", functionNameInput) : params.delete("function_name");

    const dataStartInput = document.getElementById("dataStartInput").value;
    dataStartInput ? params.set("data_start", dataStartInput.replace('T', ' ')) : params.delete("data_start");

    const dataEndInput = document.getElementById("dataEndInput").value;
    dataEndInput ? params.set("data_end", dataEndInput.replace('T', ' ')) : params.delete("data_end");

    url.search = params.toString();
    window.location.href = url.toString();
}
