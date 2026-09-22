import 'package:flutter/material.dart';
import 'config/app_config.dart';

void main() {
  AppConfig.validate();
  runApp(const CustomerApp());
}

class CustomerApp extends StatelessWidget {
  const CustomerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      title: 'Customer App',
      home: Scaffold(
        body: Center(child: Text('Customer App')),
      ),
    );
  }
}
