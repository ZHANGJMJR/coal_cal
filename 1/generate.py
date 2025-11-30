import os

# 项目根目录
project_root = "haoyun_peimei_hive_clone"

# 文件结构和内容
files = {
    "pubspec.yaml": """name: haoyun_peimei_hive_clone
description: 克隆“好云配煤”App v1.0.17 Flutter + Hive
publish_to: 'none'
version: 1.0.0+1

environment:
  sdk: ">=3.0.0 <4.0.0"

dependencies:
  flutter:
    sdk: flutter
  get: ^4.6.5
  hive: ^2.2.3
  hive_flutter: ^1.1.0
  path_provider: ^2.0.15
  fluttertoast: ^8.2.1

dev_dependencies:
  flutter_test:
    sdk: flutter
  hive_generator: ^2.0.0
  build_runner: ^2.3.3

flutter:
  uses-material-design: true
""",
    "lib/main.dart": """import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'pages/home_page.dart';
import 'models/coal_model.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Hive.initFlutter();
  Hive.registerAdapter(CoalModelAdapter());
  await Hive.openBox<CoalModel>('coalBox');
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return GetMaterialApp(
      debugShowCheckedModeBanner: false,
      title: '好云配煤克隆',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: HomePage(),
    );
  }
}
""",
    "lib/models/coal_model.dart": """import 'package:hive/hive.dart';
part 'coal_model.g.dart';

@HiveType(typeId: 0)
class CoalModel extends HiveObject {
  @HiveField(0)
  String name;

  @HiveField(1)
  double calorific;

  @HiveField(2)
  double ash;

  @HiveField(3)
  double sulfur;

  CoalModel({required this.name, required this.calorific, required this.ash, required this.sulfur});
}
""",
    "lib/controllers/coal_controller.dart": """import 'package:get/get.dart';
import 'package:hive/hive.dart';
import '../models/coal_model.dart';

class CoalController extends GetxController {
  var coalBox = Hive.box<CoalModel>('coalBox');
  var coalList = <CoalModel>[].obs;

  @override
  void onInit() {
    super.onInit();
    loadCoal();
  }

  void loadCoal() {
    coalList.value = coalBox.values.toList();
  }

  void addCoal(CoalModel coal) {
    coalBox.add(coal);
    loadCoal();
  }

  void deleteCoal(int index) {
    coalBox.deleteAt(index);
    loadCoal();
  }

  double calculateOptimal() {
    if (coalList.isEmpty) return 0;
    double total = coalList.map((c) => c.calorific).reduce((a, b) => a + b);
    return total / coalList.length;
  }
}
""",
    "lib/pages/home_page.dart": """import 'package:flutter/material.dart';
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
""",
    "lib/pages/calculate_page.dart": """import 'package:flutter/material.dart';
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
""",
    "lib/pages/result_page.dart": """import 'package:flutter/material.dart';

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
""",
    "lib/pages/history_page.dart": """import 'package:flutter/material.dart';
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
""",
    "lib/widgets/coal_card.dart": """import 'package:flutter/material.dart';
import '../models/coal_model.dart';

class CoalCard extends StatelessWidget {
  final CoalModel coal;

  CoalCard({required this.coal});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.symmetric(vertical: 8, horizontal: 16),
      child: ListTile(
        title: Text(coal.name),
        subtitle: Text(
            '发热量: ${coal.calorific}, 灰分: ${coal.ash}, 硫分: ${coal.sulfur}'),
      ),
    );
  }
}
""",
}

# 创建目录和文件
for path, content in files.items():
    full_path = os.path.join(project_root, path.replace("/", os.sep))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"项目文件已生成在 ./{project_root} 目录中")