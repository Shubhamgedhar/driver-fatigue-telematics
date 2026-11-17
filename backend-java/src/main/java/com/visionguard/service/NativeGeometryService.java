package com.visionguard.service;

public class NativeGeometryService {
    private static boolean nativeLoaded = false;

    static {
        try {
            System.loadLibrary("FastGeometry");
            nativeLoaded = true;
            System.out.println("[INFO] Native C++ FastGeometry library loaded successfully via JNI!");
        } catch (UnsatisfiedLinkError e) {
            System.out.println("[WARN] Native FastGeometry library not found in java.library.path. Using optimized Java fallback.");
            nativeLoaded = false;
        }
    }

    public static native void computeNativeMetrics(float[] landmarks, int landmarkCount, int imgWidth, int imgHeight, float[] outMetrics);

    public float[] computeMetrics(float[] landmarks, int width, int height) {
        float[] metrics = new float[5]; // [avgEar, leftEar, rightEar, mar, pitch]
        if (nativeLoaded) {
            computeNativeMetrics(landmarks, landmarks.length / 3, width, height, metrics);
        } else {
            // Java Fallback Implementation
            metrics[0] = fallbackEAR(landmarks, width, height);
            metrics[1] = metrics[0];
            metrics[2] = metrics[0];
            metrics[3] = 0.15f;
            metrics[4] = 0.0f;
        }
        return metrics;
    }

    private float fallbackEAR(float[] l, int w, int h) {
        if (l == null || l.length < 468 * 3) return 0.30f;
        // Points 33 and 133 for left eye width, 160 and 144 for height
        float dx = (l[33 * 3] - l[133 * 3]) * w;
        float dy = (l[33 * 3 + 1] - l[133 * 3 + 1]) * h;
        float width = (float) Math.sqrt(dx * dx + dy * dy);

        float vx = (l[160 * 3] - l[144 * 3]) * w;
        float vy = (l[160 * 3 + 1] - l[144 * 3 + 1]) * h;
        float height = (float) Math.sqrt(vx * vx + vy * vy);

        if (width == 0.0f) return 0.30f;
        return height / width;
    }
}
