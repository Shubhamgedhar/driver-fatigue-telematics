package com.visionguard.service;

import com.visionguard.model.ViolationEvent;
import java.util.ArrayDeque;
import java.util.Deque;

public class FatigueEngine {
    private static final float EAR_THRESHOLD = 0.20f;
    private static final int CONSECUTIVE_FRAMES_DROWSY = 40; // ~1.5 - 2.0s at 25-30 fps
    private static final float MAR_THRESHOLD = 0.65f;
    private static final float PITCH_DISTRACTION = -20.0f;

    private int lowEarCounter = 0;
    private int yawnCounter = 0;
    private long currentTripId = 1L;
    private Deque<ViolationEvent> violationHistory = new ArrayDeque<>();

    public enum DriverState {
        ATTENTIVE,
        EARLY_WARNING,
        CRITICAL_DROWSINESS,
        DISTRACTED,
        YAWNING
    }

    public synchronized DriverState evaluateFrame(float ear, float mar, float pitch) {
        DriverState state = DriverState.ATTENTIVE;

        // Drowsiness check
        if (ear < EAR_THRESHOLD) {
            lowEarCounter++;
            if (lowEarCounter >= CONSECUTIVE_FRAMES_DROWSY) {
                state = DriverState.CRITICAL_DROWSINESS;
                ViolationEvent event = new ViolationEvent(currentTripId, "MICROSLEEP", "CRITICAL", ear, lowEarCounter / 25.0);
                violationHistory.addFirst(event);
            } else if (lowEarCounter >= 15) {
                state = DriverState.EARLY_WARNING;
            }
        } else {
            lowEarCounter = Math.max(0, lowEarCounter - 2);
        }

        // Yawning check
        if (mar > MAR_THRESHOLD) {
            yawnCounter++;
            if (yawnCounter >= 30) {
                state = DriverState.YAWNING;
            }
        } else {
            yawnCounter = 0;
        }

        // Distraction check (looking at phone)
        if (pitch < PITCH_DISTRACTION) {
            state = DriverState.DISTRACTED;
        }

        return state;
    }

    public Deque<ViolationEvent> getViolationHistory() {
        return violationHistory;
    }
}
