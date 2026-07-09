let itype = 0; // index of currently active comparison type (Maps=0 or Time-Series=1)
let items = {"sim" : sims, "var" : Object.keys(vars), "freq" : map_freqs, "mod" : mods}; // interface items of currently active comparison type
let state = {"sim" : [], "var" : [0], "freq" : [0], "mod" : [0], "reg" : [0,1,2,3], "pick" : [] }; // current interface state defined by selected indices in all selectors
for (let idx=0; idx<sims.length; idx++) { state["sim"].push(idx); } // by default make all simulations selected
setType(itype);

document.addEventListener("mousedown", function(event) {
    if (event.button === 1) {   // 1 is the middle mouse button
        event.preventDefault(); // optional: prevent default middle click behavior (like auto-scroll)
        if (state["pick"].length > 0) { openSelection(); }
    }
});

function setType(newType) {
    itype = newType;
    if (types[itype] == "map") {
        items = {"sim" : sims, "var" : Object.keys(vars), "freq" : map_freqs, "mod" : mods};
    } else if (types[itype] == "ts") {
        items = {"sim" : sims, "var" : Object.keys(vars), "freq" : ts_freqs, "reg" : regs};
    }
}

function getState() {
    for (let idx=0; idx<Object.keys(items).length; idx++) {
        let item = Object.keys(items)[idx];
        let newstate = [];
        let select = document.getElementById(item+"Select");
        for (let jdx=0; jdx<select.selectedOptions.length; jdx++) { newstate.push(Number(select.selectedOptions[jdx]["id"])); }
        state[item] = newstate;
    }
}

function makeInterf() {
    let table, tr, td, text, select, option, button
    const div = document.getElementById("interf");
    const overlay = document.getElementById("overlay");
    const zoomedImage = document.getElementById("zoomedImage");
    overlay.addEventListener("click", () => {
        overlay.style.display = "none";
        zoomedImage.src = "";
    });

    // remove old elements if present
    while (div.firstChild) { div.firstChild.remove() }
    
    // Type Selector (Maps / Time-series)
    table = document.createElement("table");
    table.setAttribute("id", "typeTable");
    table.setAttribute("border", 0);
    tr = document.createElement("tr");
    for (let idx=0; idx<types.length; idx++) {
        td = document.createElement("td");
        if (idx == itype) { td.setAttribute("class", "activeMode"); }
        else { td.setAttribute("class", "inactiveMode"); }
        td.setAttribute("onclick", "setType("+idx+"); makeInterf();");
        text = document.createTextNode(labels[types[idx]]);
        td.appendChild(text);
        tr.appendChild(td);
    }
    table.appendChild(tr);
    div.appendChild(table);
    
    // Control Table
    table = document.createElement("table");
    table.setAttribute("id", "controlTable");
    table.setAttribute("border", 0);
    table.setAttribute("bgcolor", "#FFFFCC");
    table.setAttribute("cellpadding", 0);
    // Headings
    tr = document.createElement("tr");
    for (let key in items) {
        td = document.createElement("td");
        td.setAttribute("class", "interfHeader");
        text = document.createTextNode(labels[key]);
        td.appendChild(text);
        tr.appendChild(td);
    }
    table.appendChild(tr);
    // Selectors    
    tr = document.createElement("tr");
    for (let key in items) {
        td = document.createElement("td");
        td.setAttribute("valign", "top");
        td.setAttribute("style", "padding: 0px 10px 20px 10px;");
        select = document.createElement("select");
        select.setAttribute("id", key+"Select");
        select.setAttribute("size", Math.min(5, items[key].length+1));
        select.setAttribute("multiple", "multiple");
        select.addEventListener("dblclick", () => {
            getState();
            makeInterf();
            makeTable();
        });
        for (let idx=0; idx<items[key].length; idx++) {
            option = document.createElement("option");
            option.setAttribute("id", idx);
            if (state[key].includes(idx)) { option.setAttribute("selected", ""); }
            if (items[key][idx].startsWith("vs")) {
                if (items[key][idx] == "vsobs") {
                    label = "Dif vs OBS";
                } else {
                    let difsim = Number(items[key][idx].substring(2));
                    label = "Dif vs " + sims[difsim];
                }
            } else if (items[key][idx] in labels) {
                label = labels[items[key][idx]];
            } else {
                label = items[key][idx];
            }
            text = document.createTextNode(label);
            option.appendChild(text);
            select.appendChild(option);
        }
        td.appendChild(select);
        tr.appendChild(td);
    }
    table.appendChild(tr);
    div.appendChild(table);
    
    // Buttons Table
    table = document.createElement("table");
    table.setAttribute("id", "buttonTable");
    table.setAttribute("border", 0);
    table.setAttribute("cellpadding", 5);
    tr = document.createElement("tr");
    // Update Button
    td = document.createElement("td");
    button = document.createElement("button");
    button.setAttribute("onclick", "getState(); makeInterf(); makeTable();");
    text = document.createTextNode("Update Page");
    button.appendChild(text);
    td.appendChild(button);
    tr.appendChild(td);
    // Open Button
    td = document.createElement("td");
    button = document.createElement("button");
    button.setAttribute("onclick", "openSelection();");
    text = document.createTextNode("Open Image Selection");
    button.appendChild(text);
    td.appendChild(button);
    tr.appendChild(td);
    // Clear Button
    td = document.createElement("td");
    button = document.createElement("button");
    button.setAttribute("onclick", "clearSelection();");
    text = document.createTextNode("Clear Image Selection");
    button.appendChild(text);
    td.appendChild(button);
    tr.appendChild(td);
    table.appendChild(tr);
    // Console
    tr = document.createElement("tr");
    td = document.createElement("td");
    td.setAttribute("id", "myconsole");
    td.setAttribute("colspan", "3");
    text = document.createTextNode("");
    td.appendChild(text);
    tr.appendChild(td);
    table.appendChild(tr);
    div.appendChild(table);
}

function makeTable() {
    const url = window.location.href;
    const urlPath = url.substring(0, url.lastIndexOf("/") + 1);
    
    let head, table, tr, td, img, text;
    const div = document.getElementById("table");

    // remove old elements if present
    while (div.firstChild) { div.firstChild.remove() }

    for (const igroup of state["var"]) {
        let groupname = Object.keys(vars)[igroup];
        
        // heading with the title of variables group
        head = document.createElement("h1");
        text = document.createTextNode(labels[groupname]);
        head.appendChild(text);
        div.appendChild(head);
        
        table = document.createElement("table");
        for (let varname of vars[groupname]) {
            tr = document.createElement("tr");
            td = document.createElement("td");
            td.setAttribute("class", "tableHeader");
            if (types[itype] == "map") { td.setAttribute("colspan", sims.length+1); }
            else if (types[itype] == "ts") { td.setAttribute("colspan", state["reg"].length+1); }
            text = document.createTextNode(labels[varname]);
            td.appendChild(text);
            tr.appendChild(td);
            table.appendChild(tr);
            
            if (types[itype] == "map") {
                let freqnames = [];
                for (let ifreq of state["freq"]) {
                    if (map_freqs[ifreq] == "ye") { freqnames.push("anm"); }
                    else if (map_freqs[ifreq] == "3m") { freqnames.push("djf"); freqnames.push("mam"); freqnames.push("jja"); freqnames.push("son"); }
                    else if (["djf","mam","jja","son"].includes(map_freqs[ifreq])) { freqnames.push(map_freqs[ifreq]); }
                }
                let modnames = []; // list of paires (modname, obsname), where modname is a specific block in plot filename, obsname is the name of observation product which plot should be added in the last column
                for (let imod of state["mod"]) {
                    if (mods[imod] == "map") { modnames.push(["", ""]); } // for maps both modname/obsname are empty
                    else if (mods[imod] == "vsobs") {
                        if (Array.isArray(obs[varname])) {
                            for (let obsname of obs[varname]) {
                                modnames.push(["_vs_"+obsname, obsname]); // for difference-vs-obs maps for example modname="_vs_jung", obsname="jung"
                            }
                        } else {
                            modnames.push(["_vs_"+obs[varname], obs[varname]]);
                        }
                    }
                    else if (mods[imod].startsWith("vs")) {
                        let iref = Number([mods[imod].substring(2)]);
                        modnames.push(["_vs_"+sims[iref], ""]); // for difference-vs-sim for example modname="_vs_FGS.CRUJRA", obsname is empty
                    }
                }
                for (let freqname of freqnames) {
                    for (let [modname, obsname] of modnames) {
                        tr = document.createElement("tr");
                        for (let isim of state["sim"]) {
                            let simname = sims[isim];
                            let path = urlPath+pngPath+simname+modname+"_"+varname+"_"+freqname+".png";
                            if (simname == modname.substring(4)) { path = ""; } // for difference-vs-sim there are no maps for simulation vs itself, so put path to empty
                            td = document.createElement("td");
                            img = imgElement(path);
                            td.appendChild(img);
                            tr.appendChild(td);
                        }
                        if (obsname != "") {
                            let path = urlPath+pngPath+obsname+"_"+varname+"_"+freqname+".png";
                            td = document.createElement("td");
                            img = imgElement(path);
                            td.appendChild(img);
                            tr.appendChild(td);                            
                        }
                        table.appendChild(tr);
                    }
                }
            } else if (types[itype] == "ts") {
                let freqnames = [];
                for (let ifreq of state["freq"]) {
                    if (ts_freqs[ifreq] == "ye") { freqnames.push("y"); }
                    else if (ts_freqs[ifreq] == "mo") { freqnames.push("m"); }
                    else if (ts_freqs[ifreq] == "se") { freqnames.push("s"); }
                }
                let regnames = [];
                for (let ireg of state["reg"]) {
                    regnames.push(regs[ireg]);
                }
                for (let freqname of freqnames) {
                    tr = document.createElement("tr");
                    for (let regname of regnames) {
                        let path = urlPath+pngPath+varname+"_"+freqname+"_"+regname+".png";
                        td = document.createElement("td");
                        img = imgElement(path);
                        td.appendChild(img);
                        tr.appendChild(td);
                    }
                    table.appendChild(tr);
                }
            }
        }
        div.appendChild(table);
    }
}

function imgElement(path) {
    let img = document.createElement("img");
    const overlay = document.getElementById("overlay");
    const zoomedImage = document.getElementById("zoomedImage");
    img.setAttribute("id", path);
    img.setAttribute("src", path);
    img.setAttribute("width", 300);
    img.setAttribute("onerror", "this.style.display='none'");
    if (state["pick"].includes(path)) { img.setAttribute("class", "imgSelected"); }
    img.addEventListener("click", function(event) {
        zoomedImage.src = path;
        overlay.style.display = "flex";
    });
    img.addEventListener("contextmenu", function(event) {
        event.preventDefault();
        pick(path);
    });
    return img;
}

function pick(path) {
    const img = document.getElementById(path);
    if (img.getAttribute("class") == "imgSelected") {
        img.setAttribute("class", "");
        const idx = state["pick"].indexOf(path);
        if (idx > -1) { state["pick"].splice(idx, 1); }
    } else {
        img.setAttribute("class", "imgSelected");
        state["pick"].push(path);
    }
}

function openSelection() {
    const myconsole = document.getElementById("myconsole");
    myconsole.innerHTML = "";
    if (state["pick"].length == 0) { myconsole.innerHTML = "No image selected.<br>Right-click an image to select.<br>Middle-click on the page to open image selection.<br>Middle click once more to select its tab."; }
    
    let html = "";
    for (let path of state["pick"]) {
        html = html + "<img src='"+path+"'>\n";
    }    
    if (html != "") {
        let newWindow = window.open("", "myImagesComparison");
        newWindow.document.title = "My images comparison";
        
        let link = document.createElement("link");
        link.type = "text/css";
        link.rel = "stylesheet";
        link.href = "https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.11.4/themes/smoothness/jquery-ui.css"; 
        newWindow.document.getElementsByTagName("head")[0].appendChild(link);
        
        let contentStyle = "img { float: left; }\n";
        let style = newWindow.document.createElement("style");
        style.type = "text/css";
        style.appendChild(document.createTextNode(contentStyle));
        newWindow.document.getElementsByTagName("head")[0].appendChild(style);

        html = "<div id='sortable'>\n" + html + "</div>\n";
        html = html + "<div id='slider' style='width: 100px; position: fixed; bottom: 40px; right: 40px;'></div>\n";
        html = html + "<input type='text' id='sliderVal' value=2 readonly style='width: 50px; position: fixed; bottom: 15px; right: 40px; border: 0; font-weight:bold;'>\n";
        newWindow.document.body.innerHTML = html;
        
        let script = newWindow.document.createElement("script");
        script.type = "text/javascript";
        script.src = "https://cdnjs.cloudflare.com/ajax/libs/require.js/2.2.0/require.min.js";
        newWindow.document.getElementsByTagName("head")[0].appendChild(script);

        let code =  'var checkReady = function(callback) {\n' + // to wait for loading of require.js
                    '    if (window.requirejs) {\n' + 
                    '        callback();\n' +
                    '    } else {\n' + 
                    '        window.setTimeout(function() { checkReady(callback); }, 100);\n' +
                    '    }\n' +       
                    '};\n' +             
                    'checkReady(function($) {\n' + 
                    '    requirejs.config({\n' + // dependancies on jQuery and jQuery.ui
                    '        paths: {\n' +
                    '            "jquery": "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.0.0/jquery.min",\n' + 
                    '            "jqueryui": "https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.11.4/jquery-ui.min",\n' +
                    '        }\n' +
                    '    });\n' +
                    '    require(["jquery", "jqueryui"], function($) {\n' +
                    '        $(document).ready(function() {\n' +
                    '            $("#sortable").sortable();\n' + // make sortable all elements from div
                    '            var heights = $("img").map(function () { return $(this).prop("naturalHeight"); }).get();\n' +
                    '            maxHeight = Math.max.apply(null, heights);\n' + 
                    '            var widths = $("img").map(function () { return $(this).prop("naturalWidth"); }).get();\n' +
                    '            maxWidth = Math.max.apply(null, widths);\n' + 
                    '            $("#slider").slider({ value: 2, min: 1, max: 8, step: 1,\n' +
                    '                slide: function(event, ui) { \n' +
                    '                    $("#sliderVal").val(ui.value);\n' +
                    '                    $("img").css("width", (100/$("#sliderVal").val()).toFixed(3) + "%");\n'  +
                    '                    newHeight = $("img").prop("width") * maxHeight/maxWidth;\n' + // calculate the height from the rendered width prop to ratio of image h/w
                  //'                    $("img").css("height", newHeight.toFixed(3) + "px");\n'  +
                    '                }\n' +
                    '            });\n' +
                    '            $("#slider").prop("title", "Number of columns");\n' +
                    '            $("img").css("width", "50%");\n'  +
                    '            newHeight = $("img").prop("width") * maxHeight/maxWidth;\n' +
                  //'            $("img").css("height", newHeight.toFixed(3) + "px");\n'  +
                  //'            $("img").css("border", "1px solid");\n' +
                    '        });\n' +
                    '	 })\n' +
                    '});\n';
        script = newWindow.document.createElement("script");
        script.type = "text/javascript";
        script.appendChild(document.createTextNode(code));
        newWindow.document.getElementsByTagName("body")[0].appendChild(script);
        newWindow.focus();
    }
}

function clearSelection() {
    const myconsole = document.getElementById("myconsole");
    myconsole.innerHTML = "";
    for (let path of state["pick"]) {
        const img = document.getElementById(path);
        if (img) { img.setAttribute("class", ""); }
    }
    state["pick"] = [];
}

