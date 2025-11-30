import 'package:flutter/material.dart';

class ResultPage extends StatelessWidget {
  final double optimal;

  ResultPage({required this.optimal});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('计算结果')),
      body: Center(
        child: Text(
          '最优发热量: ${optimal.toStringAsFixed(2)}',
          style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
        ),
      ),
    );
  }
}
