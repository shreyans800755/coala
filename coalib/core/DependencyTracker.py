from coalib.core.Graphs import traverse_graph


class DependencyTracker:

    def __init__(self):
        self._dependency_dict = {}

    # TODO
    def __getitem__(self, item):
        """
        Returns registered
        :param item:
        :return:
        """
        # TODO
        return frozenset(self._dependency_dict[item])

    def add(self, dependency, dependant):
        """
        Add a bear-dependency to another bear manually.

        This function does not check for circular dependencies.

        :param dependency:
            The bear that is the dependency.
        :param dependant:
            The bear that is dependent.
        :raises CircularDependencyError:
            Raised when circular dependencies occur.
        """
        if dependency not in self._dependency_dict:
            self._dependency_dict[dependency] = set()

        self._dependency_dict[dependency].add(dependant)

    def resolve(self, dependency):
        """
        When a bear completes this method is called with the instance of that
        bear. The method deletes this bear from the list of dependencies of
        each bear in the dependency dictionary. It returns the bears which
        have all of its dependencies resolved.

        :param dependency:
            The dependency.
        :return:
            Returns a set of dependants whose dependencies were all resolved.
        """
        # Check if dependency has itself dependencies which aren't resolved,
        # these need to be removed too. The ones who instantiate a
        # DependencyTracker are responsible for resolving dependencies in the
        # right order. This operation does not free any dependencies.
        dependencies_to_remove = []
        for tracked_dependency, dependants in self._dependency_dict.items():
            if dependency in dependants:
                dependants.remove(dependency)

                # If dependants set is now empty, schedule dependency2 for
                # removal from dependency_dict.
                if not dependants:
                    dependencies_to_remove.append(tracked_dependency)

        for tracked_dependency in dependencies_to_remove:
            del self._dependency_dict[tracked_dependency]

        # Now free dependants which do depend on the given dependency.
        possible_freed_dependants = self._dependency_dict.pop(
            dependency, frozenset())
        non_free_dependants = set()

        for possible_freed_dependant in possible_freed_dependants:
            # Check if all dependencies of dependants from above are satisfied.
            # If so, there are no more dependencies for dependant. Thus it's
            # resolved.
            for dependants in self._dependency_dict.values():
                if possible_freed_dependant in dependants:
                    non_free_dependants.add(possible_freed_dependant)
                    break

        # Remaining dependents are officially resolved.
        return possible_freed_dependants - non_free_dependants

    def check_circular_dependencies(self):
        """
        Checks whether there are circular dependency conflicts.

        :raises CircularDependencyError:
            Raised on circular dependency conflicts.
        """
        traverse_graph(
            self._dependency_dict.keys(),
            lambda node: self._dependency_dict.get(node, frozenset()))

    @property
    def dependencies_resolved(self):
        return len(self._dependency_dict) == 0

    # TODO Make dependency_dict "private"
