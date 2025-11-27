import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'dart:async';
import 'dart:io';
import 'dart:isolate';

void main() {
  runApp(const PiZerApp());
}

class PiZerApp extends StatelessWidget {
  const PiZerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'PiZer',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF050505),
        primaryColor: const Color(0xFF00FFFF),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF00FFFF),
          secondary: Color(0xFFFF0055),
          surface: Color(0xFF121212),
        ),
        useMaterial3: true,
      ),
      home: const MainFlow(),
    );
  }
}

class MainFlow extends StatefulWidget {
  const MainFlow({super.key});

  @override
  State<MainFlow> createState() => _MainFlowState();
}

class _MainFlowState extends State<MainFlow> {
  int _pageIndex = 0;

  void _nextPage() {
    setState(() {
      _pageIndex++;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: AnimatedSwitcher(
        duration: const Duration(milliseconds: 500),
        child: _getPage(),
      ),
    );
  }

  Widget _getPage() {
    switch (_pageIndex) {
      case 0:
        return SplashScreen(onNext: _nextPage);
      case 1:
        return TermsScreen(onNext: _nextPage);
      case 2:
        return const MainScreen();
      default:
        return const MainScreen();
    }
  }
}

// --- 1. SPLASH SCREEN ---
class SplashScreen extends StatelessWidget {
  final VoidCallback onNext;
  const SplashScreen({super.key, required this.onNext});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Spacer(),
          Text(
            "πzer",
            style: GoogleFonts.helvetica(
              fontSize: 80,
              fontWeight: FontWeight.bold,
              color: const Color(0xFF00FFFF),
            ),
          ),
          const SizedBox(height: 20),
          Text(
            "Advanced Cyber Defence",
            style: GoogleFonts.helvetica(fontSize: 18, color: Colors.white),
          ),
          Text(
            "Professional Recovery Suite",
            style: GoogleFonts.helvetica(fontSize: 14, color: Colors.grey),
          ),
          const Spacer(),
          Text(
            "SYSTEM ONLINE",
            style: GoogleFonts.consolas(color: const Color(0xFF00FF41)),
          ),
          const SizedBox(height: 40),
          CyberButton(text: "INITIALIZE SYSTEM", onTap: onNext),
          const SizedBox(height: 40),
        ],
      ),
    );
  }
}

// --- 2. TERMS SCREEN ---
class TermsScreen extends StatelessWidget {
  final VoidCallback onNext;
  const TermsScreen({super.key, required this.onNext});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(30),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 60),
          Text(
            "ACCESS PROTOCOLS",
            style: GoogleFonts.helvetica(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: const Color(0xFF00FFFF),
            ),
          ),
          const SizedBox(height: 40),
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: const Color(0xFF121212),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _termItem("1. AUTHORIZED USE ONLY", "Use this tool only on files you own."),
                const SizedBox(height: 20),
                _termItem("2. NO LIABILITY", "Developers are not responsible for misuse."),
                const SizedBox(height: 20),
                _termItem("3. EDUCATIONAL PURPOSE", "Designed for security testing."),
              ],
            ),
          ),
          const Spacer(),
          CyberButton(
            text: "ACCEPT & PROCEED",
            onTap: onNext,
            color: const Color(0xFF121212),
            textColor: const Color(0xFF00FFFF),
          ),
          const SizedBox(height: 40),
        ],
      ),
    );
  }

  Widget _termItem(String title, String desc) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: GoogleFonts.consolas(fontWeight: FontWeight.bold, color: Colors.white)),
        const SizedBox(height: 5),
        Text(desc, style: GoogleFonts.consolas(color: Colors.grey)),
      ],
    );
  }
}

// --- 3. MAIN SCREEN ---
class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  String _status = "READY";
  String _currentKey = "WAITING...";
  bool _isBrute = true;
  bool _running = false;

  void _startAttack() {
    setState(() {
      _running = true;
      _status = "ATTACKING...";
      _currentKey = "INITIALIZING...";
    });

    // Simulate Attack Stream for UI Demo
    // In a real Flutter app, we'd spawn an Isolate to run the brute force logic
    Timer.periodic(const Duration(milliseconds: 50), (timer) {
      if (!_running) {
        timer.cancel();
        return;
      }
      setState(() {
        // Random "hacker" string generation for visual effect
        _currentKey = String.fromCharCodes(List.generate(6, (index) => 97 + (DateTime.now().microsecondsSinceEpoch % 26)));
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(vertical: 20),
                color: const Color(0xFF121212),
                child: Center(
                  child: Text(
                    "πzer // COMMAND",
                    style: GoogleFonts.consolas(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: const Color(0xFF00FFFF),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 30),

              // Target
              Text("TARGET ARCHIVE", style: GoogleFonts.helvetica(fontWeight: FontWeight.bold, color: Colors.grey)),
              const SizedBox(height: 10),
              Container(
                width: double.infinity,
                height: 60,
                color: const Color(0xFF121212),
                child: Center(
                  child: Text(
                    "[ TAP TO SELECT ]",
                    style: GoogleFonts.consolas(fontSize: 16, color: Colors.white),
                  ),
                ),
              ),

              const SizedBox(height: 30),

              // Config
              Text("ATTACK CONFIGURATION", style: GoogleFonts.helvetica(fontWeight: FontWeight.bold, color: Colors.grey)),
              const SizedBox(height: 10),
              Row(
                children: [
                  _modeBtn("BRUTE FORCE", _isBrute, () => setState(() => _isBrute = true)),
                  const SizedBox(width: 10),
                  _modeBtn("DICTIONARY", !_isBrute, () => setState(() => _isBrute = false)),
                ],
              ),

              const SizedBox(height: 30),

              // Stream
              Text("DECRYPTION STREAM", style: GoogleFonts.helvetica(fontWeight: FontWeight.bold, color: Colors.grey)),
              const SizedBox(height: 10),
              Container(
                width: double.infinity,
                height: 100,
                decoration: BoxDecoration(
                  color: Colors.black,
                  border: Border.all(color: const Color(0xFF121212)),
                ),
                child: Center(
                  child: Text(
                    _currentKey,
                    style: GoogleFonts.consolas(fontSize: 24, color: const Color(0xFF00FFFF)),
                  ),
                ),
              ),

              const Spacer(),
              CyberButton(
                text: "EXECUTE",
                onTap: _startAttack,
                color: const Color(0xFFFF0055),
                textColor: Colors.white,
              ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }

  Widget _modeBtn(String text, bool active, VoidCallback onTap) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 10),
          color: const Color(0xFF050505),
          child: Text(
            "[ $text ]",
            textAlign: TextAlign.center,
            style: GoogleFonts.consolas(
              fontWeight: FontWeight.bold,
              color: active ? const Color(0xFF00FFFF) : Colors.grey,
            ),
          ),
        ),
      ),
    );
  }
}

// --- WIDGETS ---
class CyberButton extends StatelessWidget {
  final String text;
  final VoidCallback onTap;
  final Color color;
  final Color textColor;

  const CyberButton({
    super.key,
    required this.text,
    required this.onTap,
    this.color = const Color(0xFF121212),
    this.textColor = const Color(0xFF00FFFF),
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        height: 60,
        width: double.infinity,
        decoration: BoxDecoration(
          color: color == const Color(0xFF121212) ? Colors.transparent : color,
          border: Border.all(color: const Color(0xFF00FFFF), width: 2),
        ),
        child: Center(
          child: Text(
            text,
            style: GoogleFonts.helvetica(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: textColor,
            ),
          ),
        ),
      ),
    );
  }
}
