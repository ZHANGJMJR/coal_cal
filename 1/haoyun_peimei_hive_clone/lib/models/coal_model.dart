import 'package:hive/hive.dart';
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
