/**
 * Intelligent Land Record Digitization & Validation System
 * Client-Side Scripts - INT253 Academic Project
 */

document.addEventListener('DOMContentLoaded', function () {
    // Live Cadastral Validation Trigger via JSON API
    const liveValidateBtn = document.getElementById('btn-run-live-ai');
    const aiResultsContainer = document.getElementById('ai-live-results');

    if (liveValidateBtn && aiResultsContainer) {
        liveValidateBtn.addEventListener('click', function () {
            const parcelSlug = this.getAttribute('data-parcel-slug');
            const apiUrl = `/api/parcels/${parcelSlug}/validate/`;

            liveValidateBtn.disabled = true;
            liveValidateBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Evaluating Cadastral Rules...';
            aiResultsContainer.classList.remove('d-none');
            aiResultsContainer.innerHTML = `
                <div class="text-center py-3">
                    <div class="spinner-border text-secondary" role="status"></div>
                    <p class="mt-2 text-muted small">Querying cadastral parameters and geospatial perimeter rules...</p>
                </div>
            `;

            fetch(apiUrl)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    liveValidateBtn.disabled = false;
                    liveValidateBtn.innerHTML = '<i class="bi bi-arrow-repeat me-1"></i> Re-Run Verification';

                    const res = data.validation_result;
                    const isPassed = res.recommended_determination === 'APPROVED';
                    const alertClass = isPassed ? 'alert-success' : (res.recommended_determination === 'CONDITIONAL' ? 'alert-warning' : 'alert-danger');

                    let checksHtml = '';
                    for (const [key, check] of Object.entries(res.detailed_checks)) {
                        const icon = check.passed ? '✓' : '✗';
                        const checkLabel = key.replace(/_/g, ' ').toUpperCase();
                        checksHtml += `
                            <li class="list-group-item d-flex justify-content-between align-items-center py-2">
                                <span class="small"><strong>${icon} ${checkLabel}</strong>: ${check.details}</span>
                                <span class="badge ${check.passed ? 'badge-verified' : 'badge-disputed'}">${check.passed ? 'Passed' : 'Failed'}</span>
                            </li>
                        `;
                    }

                    let anomaliesHtml = '';
                    if (res.anomalies_detected && res.anomalies_detected.length > 0) {
                        anomaliesHtml = `
                            <div class="mt-3">
                                <h6 class="text-danger fw-bold small">Discrepancies Flagged by Engine:</h6>
                                <ul class="text-danger small mb-0 ps-3">
                                    ${res.anomalies_detected.map(a => `<li>${a}</li>`).join('')}
                                </ul>
                            </div>
                        `;
                    } else {
                        anomaliesHtml = `<p class="text-success small mt-2 mb-0"><strong>✓ No perimeter anomalies or zoning conflicts detected.</strong></p>`;
                    }

                    const riskBadgeClass = res.risk_level === 'LOW' ? 'badge-low-risk' : (res.risk_level === 'MEDIUM' ? 'badge-medium-risk' : 'badge-high-risk');

                    aiResultsContainer.innerHTML = `
                        <div class="alert ${alertClass} border mt-2">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h6 class="alert-heading fw-bold mb-0">
                                    Cadastral Compliance Score: <strong>${res.compliance_score} / 100</strong>
                                </h6>
                                <span class="badge ${riskBadgeClass}">${res.risk_level} RISK</span>
                            </div>
                            <p class="mb-1 small"><strong>Recommended Determination:</strong> ${res.recommended_determination}</p>
                            <p class="small text-muted mb-2">${res.summary}</p>
                            
                            <h6 class="fw-bold mb-1 small">Automated Checkpoints:</h6>
                            <ul class="list-group list-group-flush border rounded bg-white">
                                ${checksHtml}
                            </ul>
                            
                            ${anomaliesHtml}

                            <div class="mt-3 d-flex justify-content-end">
                                <a href="/validation/inspect/${data.parcel.id}/" class="btn btn-sm btn-primary">
                                    Record Formal Inspection Audit &rarr;
                                </a>
                            </div>
                        </div>
                    `;
                })
                .catch(err => {
                    liveValidateBtn.disabled = false;
                    liveValidateBtn.innerHTML = '<i class="bi bi-play-circle me-1"></i> Run Live Verification';
                    aiResultsContainer.innerHTML = `
                        <div class="alert alert-danger">
                            Error contacting validation endpoint: ${err.message}
                        </div>
                    `;
                });
        });
    }
});
