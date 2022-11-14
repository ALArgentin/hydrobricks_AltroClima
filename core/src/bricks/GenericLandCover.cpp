#include "GenericLandCover.h"

GenericLandCover::GenericLandCover()
    : LandCover() {}

void GenericLandCover::AssignParameters(const BrickSettings& brickSettings) {
    Brick::AssignParameters(brickSettings);
}

void GenericLandCover::ApplyConstraints(double timeStep, bool inSolver) {
    Brick::ApplyConstraints(timeStep, inSolver);
}

void GenericLandCover::Finalize() {
    Brick::Finalize();
}
