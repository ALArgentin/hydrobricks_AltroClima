#include "Urban.h"

Urban::Urban()
    : LandCover() {}

void Urban::AssignParameters(const BrickSettings& brickSettings) {
    Brick::AssignParameters(brickSettings);
}

void Urban::ApplyConstraints(double timeStep, bool inSolver) {
    Brick::ApplyConstraints(timeStep, inSolver);
}

void Urban::Finalize() {
    Brick::Finalize();
}
