package com.visionguard.model;

import java.time.LocalDateTime;

public class ViolationEvent {
    private Long id;
    private Long tripId;
    private String violationType; // MICROSLEEP, DISTRACTION, YAWN
    private String severity;      // WARNING, CRITICAL
    private double metricValue;   // EAR or Pitch angle
    private double durationSeconds;
    private LocalDateTime timestamp;

    public ViolationEvent(Long tripId, String violationType, String severity, double metricValue, double durationSeconds) {
        this.tripId = tripId;
        this.violationType = violationType;
        this.severity = severity;
        this.metricValue = metricValue;
        this.durationSeconds = durationSeconds;
        this.timestamp = LocalDateTime.now();
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Long getTripId() { return tripId; }
    public String getViolationType() { return violationType; }
    public String getSeverity() { return severity; }
    public double getMetricValue() { return metricValue; }
    public double getDurationSeconds() { return durationSeconds; }
    public LocalDateTime getTimestamp() { return timestamp; }

    @Override
    public String toString() {
        return String.format("[%s] %s (%s) - Value: %.2f for %.1fs", 
            timestamp, violationType, severity, metricValue, durationSeconds);
    }
}
