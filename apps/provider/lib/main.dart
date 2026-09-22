import 'package:flutter/material.dart';
import 'config/app_config.dart';

void main() {
  AppConfig.validate();
  runApp(const ProviderApp());
}

class ProviderApp extends StatelessWidget {
  const ProviderApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      title: 'Provider App',
      home: Scaffold(
        body: Center(child: Text('Provider App')),
      ),
    );
  }
}
