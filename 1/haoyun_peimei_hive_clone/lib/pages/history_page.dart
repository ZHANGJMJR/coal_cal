import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../controllers/coal_controller.dart';

class HistoryPage extends StatelessWidget {
  final CoalController controller = Get.find();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('历史记录')),
      body: Obx(() {
        if (controller.coalList.isEmpty) {
          return Center(child: Text('暂无记录'));
        }
        return ListView.builder(
          itemCount: controller.coalList.length,
          itemBuilder: (context, index) {
            final coal = controller.coalList[index];
            return ListTile(
              title: Text(coal.name),
              subtitle: Text(
                  '发热量: ${coal.calorific}, 灰分: ${coal.ash}, 硫分: ${coal.sulfur}'),
              trailing: IconButton(
                icon: Icon(Icons.delete, color: Colors.red),
                onPressed: () => controller.deleteCoal(index),
              ),
            );
          },
        );
      }),
    );
  }
}
