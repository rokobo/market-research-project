if(!window.dash_clientside){window.dash_clientside={}}
const logValids=(lists,keys)=>lists.reduce((acc,_,i)=>{if(i%4===0&&keys[i/4]){acc[keys[i/4]]=lists.slice(i,i+4).flat()}return acc},{});
function haversine(a,t){var[h,n]=a,[r,s]=t,M=deg2rad(r-h),d=deg2rad(s-n),e=Math.sin(M/2)*Math.sin(M/2)+Math.cos(deg2rad(h))*Math.cos(deg2rad(r))*Math.sin(d/2)*Math.sin(d/2);return 2*Math.atan2(Math.sqrt(e),Math.sqrt(1-e))*6371}
function deg2rad(d){return d*(Math.PI/180)};
const GEOOPTS={enableHighAccuracy:true,timeout:5000,maximumAge:10000};
let LOC=null;
const getPos=(options)=>{return new Promise((resolve,reject)=>{navigator.geolocation.getCurrentPosition(resolve,reject,options)})};
const ERRS={
1:"Permita o uso de localização! Ação manual necessária!",
2:"Posição indisponível, dispositivo não conseguir determinar posição!",
3:"Dispositivo não respondeu com a localização a tempo!",
4:"Localização não é suportada nesse browser!",
default:"Erro desconhecido!"};
const ERRS2={
1: "LOCALIZAÇÃO NEGADA",
2: "POSIÇÃO INDISPONÍVEL",
3: "DISPOSITIVO LENTO",
4: "NAVEGADOR INCOMPATÍVEL",
default:"ERRO DESCONHECIDO"};
const errTxt=(e)=>{return ERRS[e]||ERRS.default};
const errTxt2=(e)=>{return ERRS2[e]||ERRS2.default};
const BR={type:"Br",namespace:"dash_html_components",props:{}};
const STRONG=(str)=>{return{type:"Strong",namespace:"dash_html_components",props:{children:str}}};
const NOUPDATE=dash_clientside.no_update;
const PRDOUT=new Array(13).fill(NOUPDATE);
function INFO(...m){ctx=dash_clientside.callback_context&&dash_clientside.callback_context.triggered_id?dash_clientside.callback_context.triggered_id:"?";console.log(`%c${INFO.caller.name.toUpperCase()} %c(${ctx}):`,"background:#00252E;color:#25F5FC","background:#382C00;color:#FFC800",...m)}
function ERROR(...m){console.log(`%cERROR ${ERROR.caller.name.toUpperCase()} %c(${dash_clientside.callback_context.triggered_id}):`,"background:#700000;color:#FFADAD","background:#382C00;color:#FFC800",...m)}
function nearest(lat,lon){smallestDist=[Infinity,""];for(est in COORDS){vals=COORDS[est];dist=haversine([lat,lon],[vals.Latitude,vals.Longitude]);if(dist<smallestDist[0]){smallestDist=[dist,est]}}return smallestDist}
function splitArgs(...args) {
    if (args.length % 2 !== 0) {throw new Error("Expected an even number of arguments.")}
    const half = args.length / 2;
    const firstHalf = args.slice(0, half);
    const secondHalf = args.slice(half);
    return [firstHalf, secondHalf];
}
function updateGeoBadge(position, error) {
    const badge = document.getElementById("geolocation-badge");
    if (!position) {
        badge.textContent = error ? errTxt2(error.code) : "Unknown error";
        badge.className = "badge bg-danger";
        return;
    }
    const { latitude, longitude } = position.coords;
    const date = new Date(position.timestamp);
    const hh = String(date.getHours()).padStart(2, '0');
    const mm = String(date.getMinutes()).padStart(2, '0');
    const ss = String(date.getSeconds()).padStart(2, '0');
    badge.textContent = `${latitude.toFixed(4)}, ${longitude.toFixed(4)} - ${hh}:${mm}:${ss}`;
    badge.className = "badge bg-secondary";

    // Load current history
    let history = [];
    try {
        const raw = localStorage.getItem("geo-history");
        if (raw) {history = JSON.parse(raw)}
    } catch { history = [] }

    // Append if moved more than 100m
    const newEntry = [latitude, longitude, position.timestamp];
    if (history.length === 0 || haversine(history.at(-1), newEntry) > 0.1) {
        history.push(newEntry);
        if (history.length > 50) history.shift(); // keep recent 50 entries
        localStorage.setItem("geo-history", JSON.stringify(history));
    }
};

function waitForBadge(elementId, callbackFn) {
    if (document.getElementById(elementId)) {callbackFn();return}
    const observer = new MutationObserver(() => { if (document.getElementById(elementId)) {observer.disconnect();callbackFn()}});
    observer.observe(document.body, { childList: true, subtree: true });
}

waitForBadge("geolocation-badge", () => {
    navigator.permissions.query({ name: 'geolocation' }).then(result => {
        if (result.state === 'denied') {updateGeoBadge(null, { code: 1, message: "Permission denied" })}
        else {navigator.geolocation.watchPosition(p => updateGeoBadge(p, null), e => {updateGeoBadge(null, e)}, GEOOPTS)}
        result.onchange = () => {location.reload()};
    });
});


function refresh_CFG() {
    console.time("refresh_CFG");
    fetch('/get-cfg')
        .then(response => {
            if (!response.ok) {throw new Error('Network response was not ok /refresh_CFG')}
            return response.json();
        })
        .then(data => { localStorage.setItem("CFG-data", JSON.stringify(data));console.timeEnd("refresh_CFG")})
        .catch(error => { console.error('Error fetching /get-cfg:', error);console.timeEnd("refresh_CFG") });
}


function refresh_brands() {
    console.time("refresh_brands");
    products = JSON.parse(localStorage.getItem("CFG-data")).products;

    // Remove brands from localStorage that are not in the current products list
    const productKeys = products.map(p => `brands-${p}`);
    Object.keys(localStorage)
        .filter(key => key.startsWith("brands-") && !productKeys.includes(key))
        .forEach(key => localStorage.removeItem(key));

    if (!products) return;
    for (const product of products) {
        fetch(`/get-brands/${product}`)
            .then(response => {
                if (!response.ok) {throw new Error(`Network response was not ok for ${product}`)}
                return response.json();
            })
            .then(data => { localStorage.setItem(`brands-${product}`, JSON.stringify(data)) })
            .catch(error => { console.error(`Error fetching /get-brand/${product}:`, error) });
    }
    console.timeEnd("refresh_brands");
}

refresh_CFG();
refresh_brands();

window.dash_clientside.functions={
theme_select: function(value) { return value },
refresh_local_storages: function(_){
    let markdown = "";
    const keys = Object.keys(localStorage).sort();
    for (const key of keys) {
        const value = localStorage.getItem(key);
        let displayValue = "";
        try {
            // Try to pretty-print JSON values
            const parsed = JSON.parse(value);
            displayValue = JSON.stringify(parsed, null, 2);
        } catch {
            // Fallback to raw value (truncate if very long)
            displayValue = value && value.length > 500 ? value.slice(0, 500) + "..." : value;
            displayValue = "``` " + displayValue + " ```";
        }
        markdown += `###### ${key}:\n\n${displayValue}\n`;
    }
    const now = new Date();
    const hh = String(now.getHours()).padStart(2, '0');
    const mm = String(now.getMinutes()).padStart(2, '0');
    const ss = String(now.getSeconds()).padStart(2, '0');
    return [markdown, `${hh}:${mm}:${ss}`];
},
validate_sections: function(name, date, estab, ...args) {
    const [color, children] = splitArgs(...args);
    let disabled = color.includes("danger")
    disabled = disabled || name === "" || date === "" || estab === "";
    disabled = disabled || name === null || date === null || estab === null;
    disabled = disabled || name === undefined || date === undefined || estab === undefined;

    counts = {};

    children.forEach(item => {
        counts[item] = (counts[item] || 0) + 1;
    });

    message = "";
    message += `✅ Produtos Perfeitos: ${counts["Completo"] || 0}\n\n`;
    message += `⚠️ Produtos com Faltas: ${counts["Faltando"] || 0}\n\n`;
    message += `❌ Produtos Sem dados: ${counts["Sem dados"] || 0}\n\n`;
    // INFO(disabled, disabled ? "danger" : "success", disabled ? "unclickable" : "", "\n", message);
    return [message, disabled, disabled ? "danger" : "success", disabled ? "unclickable" : ""];
},
load_brands: function(_, id, opts) {
    return new Promise((resolve) => {
        const prd = id.type.split("-")[1];
        const brands = JSON.parse(localStorage.getItem(`brands-${prd}`));
        if (brands === null || brands === undefined) {
            ERROR("No brands found for", prd);
            resolve([]);
        } else {
            // INFO("load_brands", prd);
            resolve(brands);
        }
    });
},
process_product_branded: function(...args) {
    return process_product(...args)
},
process_product_brandless: function(...args) {
    return process_product(...args)
},
start_listeners: function(_) {
    setupListeners();
    return NOUPDATE;
},
show_confetti: function(show) {
    if (show) {
        resetRows();
        showConfetti();
    }
    return NOUPDATE;
}
}

function showConfetti() {
    console.log("Showing confetti!");
    var duration = 10 * 1000;
    var animationEnd = Date.now() + duration;
    var defaults = { startVelocity: 30, spread: 50, ticks: 450, zIndex: 200, scalar: 1.5 };

    function randomInRange(min, max) {
    return Math.random() * (max - min) + min;
    }

    var interval = setInterval(function() {
        var timeLeft = animationEnd - Date.now();

        if (timeLeft <= 0) {
            return clearInterval(interval);
        }

        var particleCount = 30 * (timeLeft / duration);
        // since particles fall down, start a bit higher than random
        confetti({ ...defaults, particleCount, origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 } });
        confetti({ ...defaults, particleCount, origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 } });
    }, 250);
    console.log("Confetti setup complete.");
}

function waitForElementByQuery(query, timeout = 5000) {
    return new Promise((resolve, reject) => {
        const start = performance.now();
        const check = () => {
            const el = document.querySelector(query);
            if (el) return resolve(el);
            if (performance.now() - start > timeout) {
                console.error(`Timeout waiting for selector: ${query}`);
                return reject(new Error(`Timeout waiting for ${query}`));
            }
            requestAnimationFrame(check);
        };
        check();
    });
}

function waitForLocalStorage(key, timeout = 5000) {
    return new Promise((resolve, reject) => {
        const start = performance.now();
        function check() {
            const value = localStorage.getItem(key);
            if (value !== null) {
                return resolve(JSON.parse(value));
            }
            if (performance.now() - start > timeout) {
                console.error(`Timeout waiting for localStorage key: ${key}`);
                return reject(new Error(`Timeout waiting for localStorage key: ${key}`));
            }
            requestAnimationFrame(check);
        }
        check();
    });
}

function waitForElementsByQuery(query, timeout = 5000) {
    const CFG = JSON.parse(localStorage.getItem("CFG-data"));
    return new Promise((resolve, reject) => {
        const start = performance.now();
        function check() {
            const els = document.querySelectorAll(query);
            if (els && els.length >= CFG.max_rows) {
                return resolve(Array.from(els));
            }
            if (performance.now() - start > timeout) {
                console.error(`Timeout waiting for elements by selector: ${query}`);
                return reject(new Error(`Timeout waiting for elements by selector: ${query}`));
            }
            requestAnimationFrame(check);
        }
        check();
    });
}

function waitForElementById(id, timeout = 5000) {
    return new Promise((resolve, reject) => {
        const start = performance.now();
        function check() {
            const el = document.getElementById(id);
            if (el) {
                return resolve(el);
            }
            if (performance.now() - start > timeout) {
                console.error(`Timeout waiting for element with id: ${id}`);
                return reject(new Error(`Timeout waiting for element with id: ${id}`));
            }
            requestAnimationFrame(check);
        }
        check();
    });
}

async function getProductDivs() {
    console.time("getProductDivs");
    const grid = await waitForElementByQuery('[id^="grids-"]');
    const group = grid.id.split("grids-")[1];
    const productDivs = grid ? Array.from(grid.children) : [];
    console.timeEnd("getProductDivs");
    return [productDivs, group];
}

async function getProductFields(prd, group, CFG) {
    brdInputs = []
    if (CFG.product_fields[prd][0] === 1) {
        brdInputs = await waitForElementsByQuery(`select[id*="brand-${prd}-"]`)
    }
    const prcInputs = await waitForElementsByQuery(`input[id*="price-${prd}-"]`);
    const qtyInputs = await waitForElementsByQuery(`input[id*="quantity-${prd}-"]`);
    const deleteBtns = await waitForElementsByQuery(`button[id*="delete-${prd}-"]`);
    const addBtn = await waitForElementById(`add-${prd}-${group}`);
    const collapsed = await waitForElementsByQuery(`div[id*="collapse-${prd}-"]`);
    return [brdInputs, prcInputs, qtyInputs, deleteBtns, addBtn, collapsed];
}

function validateProduct(prdEvent, prd, brds, prcs, qtys, badge, icon, CFG) {
    console.time("validateProduct");

    if (brds.length === 0) {
        validBrds = Array(prcs.length).fill(true);
    } else {
        validBrds = brds.map(brd => {
            const visible = !!(brd.offsetWidth || brd.offsetHeight || brd.getClientRects().length);
            return visible ? brd.checkValidity() : true;
        });
    }
    validPrcs = prcs.map(prc => {
        const visible = !!(prc.offsetWidth || prc.offsetHeight || prc.getClientRects().length);
        return visible ? prc.checkValidity() : true;
    });
    validQtys = qtys.map(qty => {
        const visible = !!(qty.offsetWidth || qty.offsetHeight || qty.getClientRects().length);
        return visible ? qty.checkValidity() : true;
    });
    visibleRows = prcs.filter(prc => !!(prc.offsetWidth || prc.offsetHeight || prc.getClientRects().length)).length;

    let allValid = true;
    for (let i = 0; i < validBrds.length; i++) {
        if (!validBrds[i] || !validPrcs[i] || !validQtys[i]) {
            allValid = false;
            break;
        }
    }
    if (visibleRows === 0) {
        badge.textContent = "Sem dados";
        badge.className = "badge rounded-pill bg-warning";
        icon.className = "icon-orange";
    } else if (allValid) {
        if (visibleRows < CFG.product_rows[prd]) {
            badge.textContent = "Poucos itens";
            badge.className = "badge rounded-pill bg-warning";
            icon.className = "icon-orange";
        } else {
            badge.textContent = "Completo";
            badge.className = "badge rounded-pill bg-success";
            icon.className = "icon-green";
        }
    } else {
        badge.textContent = "Valores inválidos";
        badge.className = "badge rounded-pill bg-danger";
        icon.className = "icon-red";
    }
    console.timeEnd("validateProduct");
}

function addRow(prd, collapsed, initial=false) {
    console.time("addRow");
    const storageKey = `store-collapse-${prd}`;
    let storedValue = localStorage.getItem(storageKey);
    const CFG = JSON.parse(localStorage.getItem("CFG-data"));
    const expected_rows = CFG.product_rows[prd];
    let collapsedStates = collapsed.map(c => c.className.includes("show"));

    // Ensure localStorage exists, if not initialize it
    if (storedValue === null || storedValue === undefined || storedValue.length === 0 || JSON.parse(storedValue).length !== CFG.max_rows) {
        localStorage.setItem(storageKey, JSON.stringify(collapsedStates));
        storedValue = collapsedStates;
    } else {
        storedValue = JSON.parse(storedValue);
    }

    // If initial call, sync UI with localStorage
    if (initial) {
        collapsed.forEach((c, i) => {
            c.className = storedValue[i] ? "collapse show" : "collapse";
        });
        console.timeEnd("addRow");
        return;
    }

    // Add new row if possible and sync localStorage
    const nextOpenIdx = collapsedStates.findIndex(state => !state);
    if (nextOpenIdx !== -1) {
        collapsed[nextOpenIdx].className = "collapse show";
        storedValue[nextOpenIdx] = true;
    }
    localStorage.setItem(storageKey, JSON.stringify(storedValue));
    console.timeEnd("addRow");
}

function deleteRow(prd, collapsed, event, brds, prcs, qtys) {
    console.time("deleteRow");
    const storageKey = `store-collapse-${prd}`;
    let storedValue = JSON.parse(localStorage.getItem(storageKey));
    const deleteId = event.currentTarget.id;
    const deleteIdx = JSON.parse(deleteId).index;
    let collapsedStates = collapsed.map(c => c.className.includes("show"));

    // Collapse row, set field values to null and update localStorage
    if (brds.length !== 0) {brds[deleteIdx].value = null}
    prcs[deleteIdx].value = null;
    qtys[deleteIdx].value = null;
    collapsed[deleteIdx].className = "collapse";
    collapsedStates[deleteIdx] = false;
    localStorage.setItem(storageKey, JSON.stringify(collapsedStates));

    // Also change dash's persistence localStorage to null
    let key = JSON.parse(deleteId);
    console.log("Deleting row with key:", key);
    const keyBase = `_dash_persistence.${JSON.stringify(key)}.value.true`;
    const keyBrc = keyBase.replace("delete", "brand");
    const keyPrc = keyBase.replace("delete", "price");
    const keyQty = keyBase.replace("delete", "quantity");
    if (brds.length !== 0) {localStorage.setItem(keyBrc, JSON.stringify([null]))}
    localStorage.setItem(keyPrc, JSON.stringify([null]));
    localStorage.setItem(keyQty, JSON.stringify([null]));
    console.timeEnd("deleteRow");
}

async function generalValidators(group) {
    console.time("generalValidators");
    const nameInput = await waitForElementById(`collector_name-${group}`);
    const dateInput = await waitForElementById(`collection_date-${group}`);
    const estabInput = await waitForElementById(`establishment-${group}`);
    const allBadges = await waitForElementsByQuery(`span[id^="status-"][id$="${group}"]`);
    const nameIcon = await waitForElementById(`icon-collector_name-${group}`);
    const dateIcon = await waitForElementById(`icon-collection_date-${group}`);
    const estabIcon = await waitForElementById(`icon-establishment-${group}`);
    const confirmSend = await waitForElementById(`confirm-send-${group}`);
    const saveBtn = await waitForElementById(`save-products-${group}`);
    const saveContainer = await waitForElementById(`save-container-${group}`);
    console.timeEnd("generalValidators");
    return [nameInput, dateInput, estabInput, allBadges, nameIcon, dateIcon, estabIcon, confirmSend, saveBtn, saveContainer];
}

function validateSections(nameInput, dateInput, estabInput, allBadges, nameIcon, dateIcon, estabIcon, confirmSend, saveBtn, saveContainer, form, saveOverlay) {
    console.time("validateSections");

    const nameValid = nameInput.checkValidity();
    const dateValid = dateInput.checkValidity();
    const estabValid = estabInput.checkValidity();
    const badgeValids = allBadges.every(badge => {return !badge.className.includes("danger")});
    const perfectCount = allBadges.filter(badge => badge.className.includes("bg-success")).length;
    const warningCount = allBadges.filter(badge => badge.className.includes("bg-warning")).length;
    const dangerCount = allBadges.filter(badge => badge.className.includes("bg-danger")).length;

    let message = "";
    message += `✅ Produtos perfeitos: ${perfectCount}<br>`;
    message += `⚠️ Produtos com poucos itens: ${warningCount}<br>`;
    message += `❌ Produtos com dados inválidos: ${dangerCount}<br>`;
    confirmSend.innerHTML = message;

    nameIcon.className = nameValid ? "icon-green" : "icon-red";
    dateIcon.className = dateValid ? "icon-green" : "icon-red";
    estabIcon.className = estabValid ? "icon-green" : "icon-red";

    const AllValid = nameValid && dateValid && estabValid && badgeValids;

    saveBtn.className = AllValid ? "btn btn-success" : "btn btn-danger";
    saveOverlay.style.pointerEvents = AllValid ? "none" : "all";
    console.timeEnd("validateSections");
}

async function resetRows() {
    console.time("resetRows");
    const CFG = await waitForLocalStorage(`CFG-data`);
    const [productDivs, group] = await getProductDivs();
    const validators = await generalValidators(group);
    const saveOverlay = await waitForElementById(`save-overlay-${group}`);
    const form = document.querySelector("form");

    validators[0].value = "";
    validators[1].value = "";
    validators[2].value = "";

    for (const prdDiv of productDivs) {
        const prd = prdDiv.id.split("-")[0];
        const [brdInputs, prcInputs, qtyInputs, deleteBtns, addBtn, collapsed] = await getProductFields(prd, group, CFG);
        const storageKey = `store-collapse-${prd}`;
        const expected_rows = CFG.product_rows[prd];
        const max_rows = CFG.max_rows;
        const statusBadge = await waitForElementById(`status-${prd}-${group}`);
        const prdIcon = await waitForElementById(`icon-${prd}-${group}`);

        let resetCollapsed = Array.from({ length: max_rows }, (_, i) => i < expected_rows);
        localStorage.setItem(storageKey, JSON.stringify(resetCollapsed));

        collapsed.forEach((c, i) => {
            c.className = resetCollapsed[i] ? "collapse show" : "collapse";
        });

        validateProduct(null, prd, brdInputs, prcInputs, qtyInputs, statusBadge, prdIcon, CFG)
        validateSections(...validators, form, saveOverlay);
    }
    console.timeEnd("resetRows");
}

async function setupListeners() {
    /*
    In this function, we add event listeners and pre-find the elements we need.
    We really on the native validation of the input fields, so we just need to listen for changes.
    Then we use the validations to change related badges and icons.
    */
    console.time("setupListeners");
    const [productDivs, group] = await getProductDivs();
    const CFG = await waitForLocalStorage(`CFG-data`);
    const validators = await generalValidators(group);
    const saveOverlay = await waitForElementById(`save-overlay-${group}`);
    const form = document.querySelector("form");

    validators[0].addEventListener("input", function(e) {
        validateSections(...validators, form, saveOverlay);
    });
    validators[1].addEventListener("input", function(e) {
        validateSections(...validators, form, saveOverlay);
    });
    validators[2].addEventListener("input", function(e) {
        validateSections(...validators, form, saveOverlay);
    });

    for (const prdDiv of productDivs) {
        let start = performance.now();
        const prd = prdDiv.id.split("-")[0];
        const [brdInputs, prcInputs, qtyInputs, deleteBtns, addBtn, collapsed] = await getProductFields(prd, group, CFG);

        // We also need the appropriate badges and icons
        const statusBadge = await waitForElementById(`status-${prd}-${group}`);
        const prdIcon = await waitForElementById(`icon-${prd}-${group}`);

        if (brdInputs.length !== 0) {
            brdInputs.forEach(input => {
                input.addEventListener("input", function(e) {
                    validateProduct(e, prd, brdInputs, prcInputs, qtyInputs, statusBadge, prdIcon, CFG)
                    validateSections(...validators, form, saveOverlay);
                });
            });
        }
        prcInputs.forEach(input => {
            input.addEventListener("input", function(e) {
                validateProduct(e, prd, brdInputs, prcInputs, qtyInputs, statusBadge, prdIcon, CFG)
                validateSections(...validators, form, saveOverlay);
            });
        });
        qtyInputs.forEach(input => {
            input.addEventListener("input", function(e) {
                validateProduct(e, prd, brdInputs, prcInputs, qtyInputs, statusBadge, prdIcon, CFG)
                validateSections(...validators, form, saveOverlay);
            });
        });
        deleteBtns.forEach(btn => {
            btn.addEventListener("click", function(e) {
                deleteRow(prd, collapsed, e, brdInputs, prcInputs, qtyInputs);
                validateProduct(e, prd, brdInputs, prcInputs, qtyInputs, statusBadge, prdIcon, CFG);
                validateSections(...validators, form, saveOverlay);
            });
        });
        addBtn.addEventListener("click", function(e) {
            addRow(prd, collapsed);
            validateProduct(e, prd, brdInputs, prcInputs, qtyInputs, statusBadge, prdIcon, CFG)
            validateSections(...validators, form, saveOverlay);
        });

        // Initial validation
        console.log(`Finished setting up listeners in ${(performance.now() - start).toFixed(2)} ms`);
        addRow(prd, collapsed, true);
        validateProduct(null, prd, brdInputs, prcInputs, qtyInputs, statusBadge, prdIcon, CFG);
    }
    validateSections(...validators, form, saveOverlay);

    saveOverlay.addEventListener("click", function(e) {
        e.preventDefault();
        e.stopPropagation();
        form.reportValidity();
    });

    console.timeEnd("setupListeners");
}
document.querySelectorAll("form").forEach(f => f.setAttribute("autocomplete", "off"));
