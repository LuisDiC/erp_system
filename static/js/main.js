// Inicializar Tom Select al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    const config = {
        plugins: ['remove_button'], // Agrega una "X" para borrar cada etiqueta
        maxOptions: null,           // Muestra todos los resultados sin límite
        hideSelected: true          // Oculta de la lista desplegable los que ya elegiste
    };

    if (document.getElementById('proveedorPlaceholder')) {
        new TomSelect('#proveedorPlaceholder', config);
    }
    if (document.getElementById('productoPlaceholder')) {
        new TomSelect('#productoPlaceholder', config);
    }
});

// --- UTILIDADES ---
function showToast(message, type = 'danger') {
    const toastEl = document.getElementById('appToast');
    if (!toastEl) return;
    toastEl.className = `toast align-items-center text-bg-${type} border-0`;
    document.getElementById('toastMessage').innerText = message;
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}

// --- LOGIN ---
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = document.getElementById('btnLogin');
        const spinner = document.getElementById('loginSpinner');
        const alertBox = document.getElementById('loginAlert');
        
        btn.disabled = true;
        spinner.classList.remove('d-none');
        alertBox.classList.add('d-none');

        const formData = new URLSearchParams();
        formData.append('username', document.getElementById('username').value);
        formData.append('password', document.getElementById('password').value);

        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            });

            if (response.ok) {
                window.location.href = '/dashboard';
            } else {
                const err = await response.json();
                alertBox.innerText = err.detail || 'Error de autenticación';
                alertBox.classList.remove('d-none');
            }
        } catch (error) {
            alertBox.innerText = 'Error de conexión con el servidor.';
            alertBox.classList.remove('d-none');
        } finally {
            btn.disabled = false;
            spinner.classList.add('d-none');
        }
    });
}

// --- LOGOUT ---
async function logout() {
    try {
        await fetch('/logout', { method: 'POST' });
        window.location.href = '/login';
    } catch(e) { console.error(e); }
}

// --- DASHBOARD: LÓGICA DE DATOS ---
const filterForm = document.getElementById('filterForm');
if (filterForm) {
    // Setear fechas por defecto (Ej: Últimos 30 días)
    const today = new Date();
    const lastMonth = new Date();
    lastMonth.setDate(today.getDate() - 30);
    
    document.getElementById('endDate').value = today.toISOString().split('T')[0];
    document.getElementById('startDate').value = lastMonth.toISOString().split('T')[0];

    filterForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await loadData();
    });
}

function clearFilters() {
    document.getElementById('folioPlaceholder').value = '';
    document.getElementById('proveedorPlaceholder').selectedIndex = -1;
// Limpiar Tom Select
    const provSelect = document.getElementById('proveedorPlaceholder');
    if(provSelect && provSelect.tomselect) provSelect.tomselect.clear();
    
    const prodSelect = document.getElementById('productoPlaceholder');
    if(prodSelect && prodSelect.tomselect) prodSelect.tomselect.clear();
}

function getFilterParams() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    
    if (!startDate || !endDate) {
        showToast('El rango de fechas es obligatorio.', 'warning');
        return null;
    }

    const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate
    });


    const status = document.getElementById('statusPlaceholder').value;
    const proveedorSelect = document.getElementById('proveedorPlaceholder');
    const productoSelect = document.getElementById('productoPlaceholder');

    const folioStr = document.getElementById('folioPlaceholder').value;
    if (folioStr) {
        // Cortamos el texto por las comas
        const foliosArray = folioStr.split(',');
        
        foliosArray.forEach(f => {
            const val = f.trim(); // Limpiamos espacios en blanco accidentales
            
            // Validamos que no esté vacío y que sí sea un número válido antes de enviarlo
            if (val !== '' && !isNaN(val)) {
                params.append('folio', val);
            }
        });
    }

    


    if (status) params.append('status', status);
    for (let option of proveedorSelect.selectedOptions) {
        params.append('proveedor', option.value);
    }
    for (let option of productoSelect.selectedOptions) {
        params.append('producto', option.value);
    }
  
    params.append('_t', Date.now());
    return params;
}

async function loadData() {
    const params = getFilterParams();
    if (!params) return;

    params.append('_t', Date.now());



    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = `<tr><td colspan="8" class="text-center py-5"><div class="spinner-border text-primary" role="status"></div><div class="mt-2 text-muted">Cargando registros...</div></td></tr>`;

    try {
        const response = await fetch(`/api/data?${params.toString()}`);
        if (!response.ok) {
            if(response.status === 401) window.location.href = '/login';
            throw new Error('Error al consultar datos');
        }
        
        const data = await response.json();
        renderTable(data.records);
        document.getElementById('recordCount').innerText = `Total registros: ${data.total}`;
    } catch (error) {
        showToast(error.message);
        tbody.innerHTML = `<tr><td colspan="8" class="text-center py-5 text-danger"><i class="fas fa-exclamation-triangle"></i> Error al cargar datos.</td></tr>`;
    }
}

function renderTable(records) {
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';

    if (records.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center py-5 text-muted"><i class="fas fa-info-circle"></i> No se encontraron folios.</td></tr>`;
        return;
    }

    records.forEach(row => {
        const tr = document.createElement('tr');
        // El cursor pointer indica que es interactivo
        tr.style.cursor = 'pointer'; 
        // Llamada a la función del modal al hacer clic en cualquier parte de la fila
        tr.onclick = () => openFolioModal(row.Folio, row.Has_PDF);
        
        let statusBadge = 'bg-secondary';
        if(row.Status === 'COMPLETADA') statusBadge = 'bg-success';
        if(row.Status === 'CANCELADA') statusBadge = 'bg-danger';
        

        // Botón dinámico de PDF
        let pdfButton = row.Has_PDF 
            ? `<button class="btn btn-sm btn-outline-danger" onclick="descargarPDF(event, ${row.Folio})" title="Descargar PDF"><i class="fas fa-file-pdf"></i></button>` 
            : `<span class="text-muted small">N/A</span>`;

        tr.innerHTML = `
            <td class="fw-bold text-primary">${row.Folio}</td>
            <td>${row.Fecha}</td>
            <td>${row.Proveedor}</td>
            <td><div class="text-truncate text-muted small" style="max-width: 250px;">${row.Observacion}</div></td>
            <td class="text-center"><span class="badge ${statusBadge}">${row.Status}</span></td>
            <td class="text-center">${pdfButton}</td>
        `;
        tbody.appendChild(tr);
    });
}

// --- NUEVA LÓGICA DE DETALLE Y PDF ---
let modalActualFolio = null; // Variable global para el botón del modal

async function openFolioModal(folio, hasPdf) {
    modalActualFolio = folio;
    document.getElementById('modalFolioId').innerText = folio;
    
    // Configuración del botón PDF en el modal
    const btnPdf = document.getElementById('modalBtnPDF');
    if (hasPdf) {
        btnPdf.classList.remove('d-none');
    } else {
        btnPdf.classList.add('d-none');
    }

    const tbody = document.getElementById('modalTableBody');
    tbody.innerHTML = `<tr><td colspan="6" class="text-center py-3"><div class="spinner-border spinner-border-sm text-primary"></div></td></tr>`;
    
    // Abre el modal usando Bootstrap de forma nativa
    const modal = new bootstrap.Modal(document.getElementById('folioModal'));
    modal.show();

    try {
        const response = await fetch(`/api/folio/${folio}`);
        if (!response.ok) throw new Error('Error al consultar detalles');
        const data = await response.json();
        
        tbody.innerHTML = '';
        data.records.forEach(r => {
            tbody.innerHTML += `
                <tr>
                    <td class="text-end">${r.Peso_Bruto.toFixed(2)} kg</td>
                    <td class="text-end">${r.Tara.toFixed(2)} kg</td>
                    <td class="text-end fw-bold">${r.Peso_Neto.toFixed(2)} kg</td>
                    <td>${r.Descripcion}</td>
                    <td class="text-end">${r.Cantidad}</td>
                    <td class="text-end">${r.Temperatura.toFixed(1)} °C</td>
                </tr>
            `;
        });
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center text-danger py-3">Error al cargar registros.</td></tr>`;
    }
}

// Detiene la propagación del clic para que no se abra el modal si solo quieres descargar el PDF
function descargarPDF(event, folio) {
    event.stopPropagation(); 
    window.open(`/api/pdf/${folio}`, '_blank');
}

// Función conectada al botón dentro del Modal
function downloadModalPDF() {
    if (modalActualFolio) {
        window.open(`/api/pdf/${modalActualFolio}`, '_blank');
    }
}

function downloadExcel() {
    const params = getFilterParams();
    if (!params) return;
    

    params.append('_t', Date.now());

    // Crear la URL de descarga y dispararla en el navegador
    const url = `/api/export?${params.toString()}`;
    window.location.href = url;
}
