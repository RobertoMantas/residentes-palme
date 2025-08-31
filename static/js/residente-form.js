/**
 * JavaScript para el formulario de residentes
 * Maneja la preselección automática y la carga de apartamentos
 */

document.addEventListener('DOMContentLoaded', function() {
    const edificioSelect = document.getElementById('edificio_select');
    const pisoSelect = document.getElementById('piso');
    const apartamentoSelect = document.getElementById('apartamento_id');
    const apartamentoInfo = document.getElementById('apartamento_info');
    const tipoSelect = document.getElementById('tipo');
    
    // Datos de apartamentos disponibles (se cargan desde el template)
    const apartamentos = window.apartamentosData || [];
    
    function actualizarApartamentos() {
        const edificioId = edificioSelect.value;
        const piso = pisoSelect.value;
        
        // Limpiar opciones
        apartamentoSelect.innerHTML = '<option value="">Seleccione un apartamento</option>';
        apartamentoInfo.textContent = 'Seleccione un apartamento para ver la información';
        
        if (edificioId && piso) {
            const apartamentosFiltrados = apartamentos.filter(apt => 
                apt.edificio_id === edificioId && apt.piso == piso
            );
            
            if (apartamentosFiltrados.length > 0) {
                apartamentosFiltrados.forEach(apt => {
                    const option = document.createElement('option');
                    option.value = apt.id;
                    option.textContent = `Apartamento ${apt.numero}`;
                    apartamentoSelect.appendChild(option);
                });
            } else {
                apartamentoSelect.innerHTML = '<option value="">No hay apartamentos disponibles</option>';
            }
        }
    }
    
    function actualizarInfoApartamento() {
        const apartamentoId = apartamentoSelect.value;
        if (apartamentoId) {
            const apartamento = apartamentos.find(apt => apt.id === apartamentoId);
            if (apartamento) {
                apartamentoInfo.innerHTML = `
                    <strong>Edificio:</strong> ${apartamento.edificio_numero}<br>
                    <strong>Piso:</strong> ${apartamento.piso}<br>
                    <strong>Apartamento:</strong> ${apartamento.numero}
                `;
            }
        } else {
            apartamentoInfo.textContent = 'Seleccione un apartamento para ver la información';
        }
    }
    
    // Event listeners
    edificioSelect.addEventListener('change', actualizarApartamentos);
    pisoSelect.addEventListener('change', actualizarApartamentos);
    apartamentoSelect.addEventListener('change', actualizarInfoApartamento);
    
    // Si hay valores preseleccionados, cargar automáticamente los apartamentos
    if (edificioSelect.value && pisoSelect.value) {
        // Cargar apartamentos automáticamente al cargar la página
        setTimeout(function() {
            actualizarApartamentos();
        }, 100);
    }
    
    // Validación del formulario
    document.getElementById('residenteForm').addEventListener('submit', function(e) {
        const nombre = document.getElementById('nombre_completo').value.trim();
        const tipo = tipoSelect.value;
        const apartamento = apartamentoSelect.value;
        
        if (!nombre) {
            e.preventDefault();
            alert('Por favor, ingrese el nombre completo del residente.');
            return false;
        }
        
        if (!tipo) {
            e.preventDefault();
            alert('Por favor, seleccione el tipo de residente.');
            return false;
        }
        
        if (!apartamento) {
            e.preventDefault();
            alert('Por favor, seleccione un apartamento.');
            return false;
        }
        
        // Validar que se haya seleccionado edificio y piso
        if (!edificioSelect.value || !pisoSelect.value) {
            e.preventDefault();
            alert('Por favor, seleccione tanto el edificio como el piso.');
            return false;
        }
    });
});
