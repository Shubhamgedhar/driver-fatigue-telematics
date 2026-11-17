#ifndef _Included_com_visionguard_service_NativeGeometry
#define _Included_com_visionguard_service_NativeGeometry

#ifdef __cplusplus
extern "C" {
#endif

void computeNativeMetrics(const float* landmarks, int landmarkCount, int imgWidth, int imgHeight, float* outMetrics);

#ifdef __cplusplus
}
#endif

#endif
