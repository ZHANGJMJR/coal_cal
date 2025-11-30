import 'package:flutter/material.dart';
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
