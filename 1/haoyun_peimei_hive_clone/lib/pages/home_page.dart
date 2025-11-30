import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../controllers/coal_controller.dart';
import 'calculate_page.dart';
import 'history_page.dart';

class HomePage extends StatelessWidget {
  final CoalController controller = Get.put(CoalController());

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('好云配煤')),
      body: Obx(() {
        return ListView.builder(
          itemCount: controller.coalList.length,
          itemBuilder: (context, index) {
            final coal = controller.coalList[index];
            return ListTile(
              title: Text(coal.name),
              subtitle: Text('发热量: ${coal.calorific}'),
            );
          },
        );
      }),
      floatingActionButton: Column(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          FloatingActionButton(
            heroTag: 'calc',
            child: Icon(Icons.calculate),
            onPressed: () => Get.to(() => CalculatePage()),
          ),
          SizedBox(height: 10),
          FloatingActionButton(
            heroTag: 'history',
            child: Icon(Icons.history),
            onPressed: () => Get.to(() => HistoryPage()),
          ),
        ],
      ),
    );
  }
}
