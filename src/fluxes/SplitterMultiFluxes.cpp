#include "SplitterMultiFluxes.h"

SplitterMultiFluxes::SplitterMultiFluxes(HydroUnit *hydroUnit)
    : Splitter(hydroUnit)
{}

bool SplitterMultiFluxes::IsOk() {
    if (m_outputs.size() < 2) {
        wxLogError(_("SplitterMultiFluxes should have at least 2 outputs."));
        return false;
    }
    if (m_outputs.empty()) {
        wxLogError(_("SplitterMultiFluxes has no input."));
        return false;
    }

    return true;
}

void SplitterMultiFluxes::AssignParameters(const SplitterSettings &) {
    // No parameter
}

double* SplitterMultiFluxes::GetValuePointer(const wxString& name) {
    if (name.IsSameAs("output-1")) {
        return m_outputs[0]->GetAmountPointer();
    } else if (name.IsSameAs("output-2")) {
        return m_outputs[1]->GetAmountPointer();
    } else if (name.IsSameAs("output-3")) {
        return m_outputs[2]->GetAmountPointer();
    } else if (name.IsSameAs("output-4")) {
        return m_outputs[3]->GetAmountPointer();
    } else if (name.IsSameAs("output-5")) {
        return m_outputs[4]->GetAmountPointer();
    }

    throw ConceptionIssue(_("Output cannot be find."));
}

void SplitterMultiFluxes::Compute() {
    for (auto output : m_outputs) {
        output->UpdateFlux(m_inputs[0]->GetAmount());
    }
}