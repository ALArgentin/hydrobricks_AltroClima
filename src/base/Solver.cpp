#include "Solver.h"

#include "Processor.h"
#include "SolverEulerExplicit.h"
#include "SolverHeunExplicit.h"
#include "SolverRK4.h"

Solver::Solver()
    : m_processor(nullptr),
      m_nIterations(1)
{}

Solver* Solver::Factory(const SolverSettings &solverSettings) {
    if (solverSettings.name.IsSameAs("RK4", false) ||
        solverSettings.name.IsSameAs("Runge-Kutta", false) ||
        solverSettings.name.IsSameAs("RungeKutta", false)) {
        return new SolverRK4();
    } else if (solverSettings.name.IsSameAs("EulerExplicit", false) ||
               solverSettings.name.IsSameAs("Euler Explicit", false)) {
        return new SolverEulerExplicit();
    } else if (solverSettings.name.IsSameAs("HeunExplicit", false) ||
               solverSettings.name.IsSameAs("Heun Explicit", false)) {
        return new SolverHeunExplicit();
    }
    throw InvalidArgument(_("Incorrect solver name."));
}

void Solver::InitializeContainers() {
    m_stateVariables.resize(m_processor->GetNbStateVariables(), m_nIterations);
    m_changeRates.resize(m_processor->GetNbConnections(), m_nIterations);
}