#!/usr/bin/env python3

# https://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html
# https://blog.oddbit.com/post/2019-04-25-writing-ansible-filter-plugins/
# https://www.dasblinkenlichten.com/creating-ansible-filter-plugins/

class FilterModule(object):
  def filters(self):
    return {
      'test_unique': self.filter_unique,
      # Chocolatey packages
      'to_package': self.ChocolateyPackages,
      'from_package': self.ChocolateyPackageNames,
      'diff_package': self.ChocolateyPackageDifference,
      'path_join': self.path_join
    }


  def filter_unique(self, things):
    seen = set()
    unique_things = []

    for thing in things:
      if thing not in seen:
        seen.add(thing)
        unique_things.append(thing)

    return unique_things


  def ChocolateyPackages(self, package_names):
    packages = []
    if not isinstance(package_names, list) or len(package_names) == 0:
      return packages
    
    for name in package_names:
      packages.append({ 'name': name })
    
    return packages


  # Similar to json_query('[*].name')
  def ChocolateyPackageNames(self, packages):
    package_names = []
    if not isinstance(packages, list) or len(packages) == 0:
      return package_names
    
    for package in packages:
      if isinstance(package, dict) and ('name' in package):
        # Value must be called as dict keys (.get), not attributes
        if ('pseudo_name' in package):
          package_names.append(package.get('pseudo_name'))
        else:
          package_names.append(package.get('name'))
    
    return package_names


  # Main cause for using custom filters
  def ChocolateyPackageDifference(self, packages, package_names):
    results = []
    if not isinstance(packages, list) or len(packages) == 0:
      return results
    
    for package in packages:
      if isinstance(package, dict):
        if ('pseudo_name' in package):
          package_name = package.get('pseudo_name')
        else:
          package_name = package.get('name')
      elif isinstance(package, str):
        package_name = package
      # Only carry forward packages matching name
      if package_name and not (package_name in package_names):
        results.append(package)

    return results


  def path_join(self, *args):
    import os
    path = os.path.join(*args)
    result = path.rstrip("/")
    return result
