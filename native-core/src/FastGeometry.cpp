#include <cmath>
#include <vector>
#include <iostream>
#include "../include/NativeGeometry.h"

struct Point3D {
    float x, y, z;
};

inline float euclideanDist(const Point3D& p1, const Point3D& p2) {
    float dx = p1.x - p2.x;
    float dy = p1.y - p2.y;
    return std::sqrt(dx * dx + dy * dy);
}

static const int LEFT_EYE_IDX[6]  = {33, 160, 158, 133, 153, 144};
static const int RIGHT_EYE_IDX[6] = {362, 385, 387, 263, 373, 380};
static const int MOUTH_IDX[4]     = {61, 291, 13, 14};

float calculateEAR(const float* rawLandmarks, const int* idx, int w, int h) {
    Point3D p[6];
    for (int i = 0; i < 6; ++i) {
        int index = idx[i];
        p[i].x = rawLandmarks[index * 3]     * w;
        p[i].y = rawLandmarks[index * 3 + 1] * h;
    }
    float v1 = euclideanDist(p[1], p[5]);
    float v2 = euclideanDist(p[2], p[4]);
    float horiz = euclideanDist(p[0], p[3]);
    if (horiz == 0.0f) return 0.0f;
    return (v1 + v2) / (2.0f * horiz);
}

float calculateMAR(const float* rawLandmarks, const int* idx, int w, int h) {
    Point3D p[4];
    for (int i = 0; i < 4; ++i) {
        int index = idx[i];
        p[i].x = rawLandmarks[index * 3]     * w;
        p[i].y = rawLandmarks[index * 3 + 1] * h;
    }
    float vert = euclideanDist(p[2], p[3]);
    float horiz = euclideanDist(p[0], p[1]);
    if (horiz == 0.0f) return 0.0f;
    return vert / (2.0f * horiz);
}

extern "C" {

void computeNativeMetrics(const float* landmarks, int landmarkCount, int imgWidth, int imgHeight, float* outMetrics) {
    if (landmarks == nullptr || outMetrics == nullptr || landmarkCount < 468) {
        return;
    }

    float leftEar  = calculateEAR(landmarks, LEFT_EYE_IDX, imgWidth, imgHeight);
    float rightEar = calculateEAR(landmarks, RIGHT_EYE_IDX, imgWidth, imgHeight);
    float avgEar   = (leftEar + rightEar) / 2.0f;
    float mar      = calculateMAR(landmarks, MOUTH_IDX, imgWidth, imgHeight);

    float noseY = landmarks[1 * 3 + 1] * imgHeight;
    float leftEyeY = landmarks[33 * 3 + 1] * imgHeight;
    float rightEyeY = landmarks[263 * 3 + 1] * imgHeight;
    float eyeMidY = (leftEyeY + rightEyeY) / 2.0f;
    float pitchApprox = (noseY - eyeMidY) - 45.0f;

    outMetrics[0] = avgEar;
    outMetrics[1] = leftEar;
    outMetrics[2] = rightEar;
    outMetrics[3] = mar;
    outMetrics[4] = pitchApprox;
}

}
