import 'package:get/get.dart';
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
