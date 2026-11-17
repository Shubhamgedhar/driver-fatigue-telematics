package com.visionguard;

import com.visionguard.service.FatigueEngine;
import com.visionguard.service.NativeGeometryService;
import com.visionguard.model.ViolationEvent;

import java.io.*;
import java.net.*;
import java.time.format.DateTimeFormatter;

public class VisionGuardApplication {
    private static final int PORT = 8085;

    public static void main(String[] args) {
        System.out.println("============================================================");
        System.out.println("  VisionGuard: Java Concurrency & State Machine Backend     ");
        System.out.println("  Listening for Vision Telemetry on TCP Port: " + PORT);
        System.out.println("============================================================");

        NativeGeometryService nativeService = new NativeGeometryService();
        FatigueEngine fatigueEngine = new FatigueEngine();

        try (ServerSocket serverSocket = new ServerSocket(PORT)) {
            System.out.println("[READY] Java Server started. Waiting for Python Vision Engine...");

            while (true) {
                Socket clientSocket = serverSocket.accept();
                System.out.println("[CONNECTED] Inbound connection from: " + clientSocket.getRemoteSocketAddress());

                // Handle client in multithreaded worker thread
                new Thread(() -> handleClient(clientSocket, fatigueEngine, nativeService)).start();
            }
        } catch (IOException e) {
            System.err.println("[ERROR] Server error: " + e.getMessage());
        }
    }

    private static void handleClient(Socket socket, FatigueEngine engine, NativeGeometryService nativeService) {
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
             PrintWriter writer = new PrintWriter(socket.getOutputStream(), true)) {

            String line;
            while ((line = reader.readLine()) != null) {
                if (line.trim().isEmpty()) continue;

                // Expected format: EAR,MAR,PITCH
                String[] parts = line.split(",");
                if (parts.length >= 3) {
                    float ear = Float.parseFloat(parts[0]);
                    float mar = Float.parseFloat(parts[1]);
                    float pitch = Float.parseFloat(parts[2]);

                    FatigueEngine.DriverState state = engine.evaluateFrame(ear, mar, pitch);

                    // Send response back
                    String response = String.format("{"state":"%s","ear":%.3f,"mar":%.3f,"violations":%d}",
                            state.name(), ear, mar, engine.getViolationHistory().size());
                    writer.println(response);

                    if (state == FatigueEngine.DriverState.CRITICAL_DROWSINESS) {
                        System.out.println("[ALERT] >>> CRITICAL DROWSINESS DETECTED! EAR: " + ear + " <<<");
                    }
                }
            }
        } catch (Exception e) {
            System.out.println("[DISCONNECTED] Client session ended.");
        }
    }
}
