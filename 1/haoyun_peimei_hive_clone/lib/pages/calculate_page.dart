import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../controllers/coal_controller.dart';
import 'result_page.dart';
import '../models/coal_model.dart';

class CalculatePage extends StatelessWidget {
  final CoalController controller = Get.find();

  final TextEditingController nameController = TextEditingController();
  final TextEditingController calorificController = TextEditingController();
  final TextEditingController ashController = TextEditingController();
  final TextEditingController sulfurController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('添加煤种')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: nameController,
              decoration: InputDecoration(labelText: '煤种名称'),
            ),
            TextField(
              controller: calorificController,
              decoration: InputDecoration(labelText: '发热量'),
              keyboardType: TextInputType.number,
            ),
            TextField(
              controller: ashController,
              decoration: InputDecoration(labelText: '灰分'),
              keyboardType: TextInputType.number,
            ),
            TextField(
              controller: sulfurController,
              decoration: InputDecoration(labelText: '硫分'),
              keyboardType: TextInputType.number,
            ),
            SizedBox(height: 20),
            ElevatedButton(
              child: Text('计算最优配比'),
              onPressed: () {
                final coal = CoalModel(
                  name: nameController.text,
                  calorific: double.tryParse(calorificController.text) ?? 0,
                  ash: double.tryParse(ashController.text) ?? 0,
                  sulfur: double.tryParse(sulfurController.text) ?? 0,
                );
                controller.addCoal(coal);
                double optimal = controller.calculateOptimal();
                Get.to(() => ResultPage(optimal: optimal));
              },
            )
          ],
        ),
      ),
    );
  }
}
