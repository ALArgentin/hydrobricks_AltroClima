#include "ProcessOutflowLinear.h"

#include "Brick.h"
#include "WaterContainer.h"

ProcessOutflowLinear::ProcessOutflowLinear(WaterContainer* container)
    : ProcessOutflow(container),
      m_responseFactor(nullptr) {}

void ProcessOutflowLinear::SetParameters(const ProcessSettings& processSettings) {
    Process::SetParameters(processSettings);
    m_responseFactor = GetParameterValuePointer(processSettings, "response_factor");
}

vecDouble ProcessOutflowLinear::GetRates() {
    return {(*m_responseFactor) * m_container->GetContentWithChanges()};
}
