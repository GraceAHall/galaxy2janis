


from galaxy_interaction.cmdstrings.jobs.JobFactorytest import JobFactory



class WorkflowJobFactory(JobFactory):
    pass

    def refresh_attributes(self, app: MockApp, test: ToolTestDescription, xmltool: XMLToolDefinition) -> None:
        self.app = app
        self.test = test
        self.xmltool = xmltool
        self.job = Job()